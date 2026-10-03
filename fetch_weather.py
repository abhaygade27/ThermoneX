import pandas as pd
import requests
import time
import os

INPUT_FILE = "mumbai_weather_points_final_005_v2.csv"
OUTPUT_FILE = "mumbai_weather_5day_005.csv"

API = "https://api.open-meteo.com/v1/forecast"

BATCH_SIZE = 50

# Wait between successful API requests
REQUEST_DELAY = 7

# Retry settings for rate limiting
MAX_RETRIES = 6

hourly = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance"
]


print("Reading weather points...")
points = pd.read_csv(INPUT_FILE)

print(f"Weather points: {len(points)}")
print(f"Batch size: {BATCH_SIZE}")
print(
    f"Total batches: "
    f"{(len(points) + BATCH_SIZE - 1) // BATCH_SIZE}"
)


# ---------------------------------------------------------
# CHECK FOR PREVIOUSLY DOWNLOADED DATA
# ---------------------------------------------------------

downloaded_ids = set()

if os.path.exists(OUTPUT_FILE):

    print("\nExisting weather file found.")

    existing = pd.read_csv(
        OUTPUT_FILE,
        usecols=["point_id"]
    )

    downloaded_ids = set(
        existing["point_id"].astype(str)
    )

    print(
        f"Already downloaded points: "
        f"{len(downloaded_ids)}"
    )

else:

    print("\nNo previous weather file found.")
    print("Starting from the beginning.")


# ---------------------------------------------------------
# PROCESS BATCHES
# ---------------------------------------------------------

for start in range(0, len(points), BATCH_SIZE):

    batch = points.iloc[start:start + BATCH_SIZE].copy()

    # Remove points that were already successfully downloaded
    batch = batch[
        ~batch["id"].astype(str).isin(downloaded_ids)
    ]

    if len(batch) == 0:

        print(
            f"\nSkipping batch "
            f"{start + 1} to "
            f"{min(start + BATCH_SIZE, len(points))} "
            f"(already downloaded)"
        )

        continue


    print(
        f"\nProcessing points "
        f"{start + 1} to "
        f"{min(start + BATCH_SIZE, len(points))}..."
    )

    latitudes = batch["X"].tolist()
    longitudes = batch["Y"].tolist()


    params = {
        "latitude": ",".join(map(str, latitudes)),
        "longitude": ",".join(map(str, longitudes)),
        "hourly": ",".join(hourly),
        "wind_speed_unit": "ms",
        "temperature_unit": "celsius",
        "forecast_days": 5,
        "timezone": "Asia/Kolkata"
    }


    # -----------------------------------------------------
    # API REQUEST WITH RETRY
    # -----------------------------------------------------

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = requests.get(
                API,
                params=params,
                timeout=120
            )


            if response.status_code == 429:

                wait_time = 15 * attempt

                print(
                    f"Rate limited (429). "
                    f"Waiting {wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue


            response.raise_for_status()

            data = response.json()

            break


        except requests.exceptions.RequestException as e:

            print(
                f"Request failed "
                f"(attempt {attempt}/{MAX_RETRIES}): "
                f"{e}"
            )

            if attempt == MAX_RETRIES:

                print(
                    "Maximum retries reached. "
                    "Stopping safely."
                )

                raise

            wait_time = 10 * attempt

            print(
                f"Waiting {wait_time} seconds before retry..."
            )

            time.sleep(wait_time)


    # -----------------------------------------------------
    # HANDLE SINGLE/MULTIPLE LOCATION RESPONSE
    # -----------------------------------------------------

    if not isinstance(data, list):

        data = [data]


    batch_records = []


    for point_info, weather in zip(
        batch.itertuples(index=False),
        data
    ):

        times = weather["hourly"]["time"]


        for i, dt in enumerate(times):

            batch_records.append({

                "point_id": point_info.id,

                "latitude": point_info.X,

                "longitude": point_info.Y,

                "datetime": dt,

                "temperature_C":
                    weather["hourly"]["temperature_2m"][i],

                "relative_humidity_%":
                    weather["hourly"]["relative_humidity_2m"][i],

                "wind_speed_ms":
                    weather["hourly"]["wind_speed_10m"][i],

                "shortwave_radiation_Wm2":
                    weather["hourly"]["shortwave_radiation"][i],

                "direct_radiation_Wm2":
                    weather["hourly"]["direct_radiation"][i],

                "diffuse_radiation_Wm2":
                    weather["hourly"]["diffuse_radiation"][i],

                "direct_normal_irradiance_Wm2":
                    weather["hourly"]["direct_normal_irradiance"][i]
            })


    batch_df = pd.DataFrame(batch_records)


    # -----------------------------------------------------
    # SAVE IMMEDIATELY
    # -----------------------------------------------------

    file_exists = os.path.exists(OUTPUT_FILE)


    batch_df.to_csv(
        OUTPUT_FILE,
        mode="a",
        header=not file_exists,
        index=False
    )


    downloaded_ids.update(
        batch_df["point_id"].astype(str).unique()
    )


    print(
        f"Saved {len(batch_df)} records."
    )

    print(
        f"Total points completed: "
        f"{len(downloaded_ids)} / {len(points)}"
    )

    print(
        f"Total records approximately: "
        f"{len(downloaded_ids) * 120}"
    )


    # -----------------------------------------------------
    # WAIT BEFORE NEXT REQUEST
    # -----------------------------------------------------

    print(
        f"Waiting {REQUEST_DELAY} seconds "
        f"before next request..."
    )

    time.sleep(REQUEST_DELAY)


# ---------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------

print("\n========================================")
print("WEATHER DOWNLOAD COMPLETE")
print("========================================")

print(
    f"Weather points: {len(points)}"
)

print(
    f"Downloaded points: {len(downloaded_ids)}"
)

print(
    f"Expected records: {len(points) * 120}"
)

if os.path.exists(OUTPUT_FILE):

    final_df = pd.read_csv(
        OUTPUT_FILE
    )

    print(
        f"Actual records: {len(final_df)}"
    )

print("\nOutput saved to:")
print(OUTPUT_FILE)