import pandas as pd
import numpy as np
from pythermalcomfort.models import utci


# ============================================================
# CONSTANTS
# ============================================================

SIGMA = 5.670374419e-8       # Stefan-Boltzmann constant
ALPHA = 0.70                 # Shortwave absorption of human body
EPSILON = 0.97               # Longwave emissivity of human body
FA = 0.50                    # Sky/ground angle factor
GROUND_ALBEDO = 0.20         # Assumed ground reflectivity
IST_MERIDIAN = 82.5          # India Standard Time meridian


# ============================================================
# SOLAR POSITION
# ============================================================

def solar_zenith_angle(timestamp, latitude, longitude):

    # Day of year
    day_of_year = timestamp.dayofyear

    # Decimal hour
    hour = (
        timestamp.hour
        + timestamp.minute / 60
        + timestamp.second / 3600
    )

    # Fractional year
    gamma = (
        2 * np.pi / 365
        * (day_of_year - 1 + (hour - 12) / 24)
    )

    # Solar declination
    declination = (
        0.006918
        - 0.399912 * np.cos(gamma)
        + 0.070257 * np.sin(gamma)
        - 0.006758 * np.cos(2 * gamma)
        + 0.000907 * np.sin(2 * gamma)
        - 0.002697 * np.cos(3 * gamma)
        + 0.001480 * np.sin(3 * gamma)
    )

    # Equation of time (minutes)
    equation_of_time = (
        229.18
        * (
            0.000075
            + 0.001868 * np.cos(gamma)
            - 0.032077 * np.sin(gamma)
            - 0.014615 * np.cos(2 * gamma)
            - 0.040849 * np.sin(2 * gamma)
        )
    )

    # Convert local IST time to solar time
    time_correction = (
        equation_of_time
        + 4 * (longitude - IST_MERIDIAN)
    )

    solar_time_minutes = hour * 60 + time_correction

    # Solar hour angle
    hour_angle = np.radians(
        (solar_time_minutes / 4) - 180
    )

    latitude_rad = np.radians(latitude)

    # Cosine of solar zenith angle
    cos_zenith = (
        np.sin(latitude_rad) * np.sin(declination)
        + np.cos(latitude_rad)
        * np.cos(declination)
        * np.cos(hour_angle)
    )

    cos_zenith = np.clip(cos_zenith, -1, 1)

    return np.arccos(cos_zenith)


# ============================================================
# PROJECTED AREA FACTOR
# ============================================================

def projected_area_factor(zenith_angle):

    # Solar elevation in degrees
    elevation = 90 - np.degrees(zenith_angle)

    # No direct solar exposure below horizon
    if elevation <= 0:
        return 0.0

    # Published standing/walking human projection factor
    fp = (
        0.308
        * np.cos(
            np.radians(elevation)
            * (
                0.998
                - elevation ** 2 / 50000
            )
        )
    )

    return fp


# ============================================================
# MEAN RADIANT TEMPERATURE
# ============================================================

def calculate_mrt(row):

    ta = row["temperature_C"]

    ghi = max(row["shortwave_radiation_Wm2"], 0)
    diffuse = max(row["diffuse_radiation_Wm2"], 0)
    dni = max(row["direct_normal_irradiance_Wm2"], 0)

    latitude = row["latitude"]
    longitude = row["longitude"]

    timestamp = pd.Timestamp(row["datetime"])

    # Solar zenith angle
    zenith = solar_zenith_angle(
        timestamp,
        latitude,
        longitude
    )

    cos_zenith = np.cos(zenith)

    # --------------------------------------------------------
    # Direct radiation on surface perpendicular to sun rays
    # --------------------------------------------------------

    if cos_zenith > 0.05:

        direct_normal = dni

        # Projected area factor of standing/walking person
        fp = projected_area_factor(zenith)

    else:

        direct_normal = 0.0
        fp = 0.0

    # --------------------------------------------------------
    # Ground reflected radiation
    # --------------------------------------------------------

    reflected = GROUND_ALBEDO * ghi

    # --------------------------------------------------------
    # Longwave radiation
    #
    # We don't have measured urban surface temperatures.
    # Therefore, for this prototype, surrounding longwave
    # radiation is approximated from air temperature.
    # --------------------------------------------------------

    ta_kelvin = ta + 273.15

    longwave = SIGMA * ta_kelvin ** 4

    down_longwave = longwave
    up_longwave = longwave

    # --------------------------------------------------------
    # Outdoor MRT equation
    #
    # MRT = [
    #   1/sigma *
    #   (
    #     FA*(LW_down + LW_up)
    #     +
    #     (alpha/epsilon) *
    #     (
    #       FA*diffuse
    #       + FA*reflected
    #       + fp*direct_normal
    #     )
    #   )
    # ]^(1/4)
    # --------------------------------------------------------

    radiation_term = (
        FA * down_longwave
        + FA * up_longwave
        + (ALPHA / EPSILON)
        * (
            FA * diffuse
            + FA * reflected
            + fp * direct_normal
        )
    )

    mrt_kelvin = (
        radiation_term / SIGMA
    ) ** 0.25

    mrt = mrt_kelvin - 273.15

    return mrt


# ============================================================
# UTCI
# ============================================================

def calculate_utci(row):

    wind = max(
        row["wind_speed_ms"],
        0.5
    )

    result = utci(
        tdb=row["temperature_C"],
        tr=row["MRT_C"],
        v=wind,
        rh=row["relative_humidity_%"],
        units="SI",
        limit_inputs=True,
        round_output=False
    )

    return result.utci


# ============================================================
# MAIN
# ============================================================

INPUT_FILE = "mumbai_weather_5day_005.csv"
OUTPUT_FILE = "mumbai_utci_5day_005.csv"

print("Reading weather data...")

df = pd.read_csv(INPUT_FILE)

print(f"Records: {len(df)}")


# Calculate MRT
print("Calculating Mean Radiant Temperature...")

df["MRT_C"] = df.apply(
    calculate_mrt,
    axis=1
)


# Calculate UTCI
print("Calculating UTCI...")

df["UTCI_C"] = df.apply(
    calculate_utci,
    axis=1
)


# Save
df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# VALIDATION
# ============================================================

print("\n========================================")
print("DAYTIME UTCI VALIDATION")
print("========================================")

df["datetime"] = pd.to_datetime(df["datetime"])

sample_point = df["point_id"].iloc[0]

sample = df[
    (df["point_id"] == sample_point)
    & (df["datetime"].dt.hour >= 7)
    & (df["datetime"].dt.hour <= 18)
]

print(
    sample[
        [
            "datetime",
            "temperature_C",
            "wind_speed_ms",
            "shortwave_radiation_Wm2",
            "MRT_C",
            "UTCI_C"
        ]
    ].to_string(index=False)
)


# ============================================================
# OVERALL STATISTICS
# ============================================================

print("\n========================================")
print("OVERALL STATISTICS")
print("========================================")

print(
    f"MRT range: "
    f"{df['MRT_C'].min():.2f} "
    f"to "
    f"{df['MRT_C'].max():.2f} °C"
)

print(
    f"UTCI range: "
    f"{df['UTCI_C'].min():.2f} "
    f"to "
    f"{df['UTCI_C'].max():.2f} °C"
)

print(
    f"Average UTCI: "
    f"{df['UTCI_C'].mean():.2f} °C"
)

print("\nOutput saved to:")
print(OUTPUT_FILE)