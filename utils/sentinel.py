import ee
import datetime
import json

# ----------------------------
# AUTHENTICATE USING SERVICE ACCOUNT
# ----------------------------

# Path to your JSON key file
import json
import os

raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

if not raw_json:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set in environment.")

service_account_info = json.loads(raw_json)

credentials = ee.ServiceAccountCredentials(
    service_account_info["client_email"], 
    key_data=service_account_info)
# Initialize Earth Engine with service account
ee.Initialize(credentials)

# ----------------------------
# FUNCTION TO FETCH FEATURES
# ----------------------------

def get_satellite_features(lat, lon, date_str):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    start_date = date.strftime("%Y-%m-%d")
    end_date = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    point = ee.Geometry.Point([lon, lat])

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )

    image = collection.first()
    if image is None:
        raise ValueError("No valid Sentinel-2 image found for the given location and date.")

    B1 = image.select("B1")
    B2 = image.select("B2")
    B3 = image.select("B3")
    B4 = image.select("B4")
    B5 = image.select("B5")
    B6 = image.select("B6")
    B7 = image.select("B7")
    B8 = image.select("B8")
    B9 = image.select("B9")
    B11 = image.select("B11")
    B12 = image.select("B12")

    NDVI_G = image.normalizedDifference(["B8", "B3"]).rename("NDVI_G")
    NDWI = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    PSRI = image.expression("(B4 - B2) / B6", {"B2": B2, "B4": B4, "B6": B6}).rename("PSRI")
    TBVI1 = image.expression("(B6 + 0.5 * B5 - 0.5 * B2) / 2", {"B2": B2, "B5": B5, "B6": B6}).rename("TBVI1")
    NDVIRE1n = image.normalizedDifference(["B8", "B5"]).rename("NDVIRE1n")
    NDVIRE2n = image.normalizedDifference(["B8", "B6"]).rename("NDVIRE2n")
    NDVIRE3n = image.normalizedDifference(["B8", "B7"]).rename("NDVIRE3n")
    SR_n2 = image.expression("B8 / B4", {"B8": B8, "B4": B4}).rename("SR_n2")
    SR_N = image.expression("B8 / B5", {"B8": B8, "B5": B5}).rename("SR_N")
    BI = image.expression("sqrt(B11**2 + B12**2) / 2", {"B11": B11, "B12": B12}).rename("BI")
    CI = NDVIRE2n
    SI = image.expression("B11 / B12", {"B11": B11, "B12": B12}).rename("SI")
    B8_minus_B4 = image.expression("B8 - B4", {"B8": B8, "B4": B4}).rename("B8_minus_B4")
    NDVI_G_times_PSRI = NDVI_G.multiply(PSRI).rename("NDVI_G_times_PSRI")

    all_bands = image.addBands([
        NDVI_G, NDWI, PSRI, TBVI1,
        NDVIRE1n, NDVIRE2n, NDVIRE3n,
        SR_n2, SR_N, BI, CI, SI,
        B8_minus_B4, NDVI_G_times_PSRI
    ])

    sampled = all_bands.sample(point, scale=10).first().getInfo()
    if not sampled:
        raise ValueError("No data found at the given point and date.")

    props = sampled["properties"]
    return {
        "latitude": lat, "longitude": lon,
        "B1": props["B1"], "B2": props["B2"], "B3": props["B3"], "B4": props["B4"],
        "B5": props["B5"], "B6": props["B6"], "B7": props["B7"], "B8": props["B8"],
        "B9": props["B9"], "B11": props["B11"], "B12": props["B12"],
        "NDVI_G": props["NDVI_G"], "NDWI": props["NDWI"], "PSRI": props["PSRI"],
        "TBVI1": props["TBVI1"], "NDVIRE1n": props["NDVIRE1n"],
        "NDVIRE2n": props["NDVIRE2n"], "NDVIRE3n": props["NDVIRE3n"],
        "SR_n2": props["SR_n2"], "SR_N": props["SR_N"], "BI": props["BI"],
        "CI": props["NDVIRE2n"], "SI": props["SI"],
        "B8_minus_B4": props["B8_minus_B4"],
        "NDVI_G_times_PSRI": props["NDVI_G_times_PSRI"]
    }
