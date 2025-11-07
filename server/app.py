from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from global_land_mask import globe

app = Flask(__name__)
CORS(app)

FLORIDA_BOUNDS = {
    "lat_min": 24.45,
    "lat_max": 31.00,
    "lon_min": -87.63,
    "lon_max": -80.03
}
DATA_FILE = "hurdat2-1851-2024-040425.txt"
DEFAULT_EXPORT_PATH = "florida_landfall_hurricanes.csv"

def is_in_florida(lat, lon):
    """
    Check if given latitude and longitude falls within bounding box of the state of Florida.

    Args:
        lat (float): Latitude 
        lon (float): Longitude

    Returns:
        bool: True if inside, else False.
    """
    return (FLORIDA_BOUNDS["lat_min"] <= lat <= FLORIDA_BOUNDS["lat_max"] and
            FLORIDA_BOUNDS["lon_min"] <= lon <= FLORIDA_BOUNDS["lon_max"])

def parse_hurdat2(file):
    """
    Parse a hurdat2 file and extract hurricanes that made landfall in Florida using L indicator from the data file.

    Args:
        file (str): Path to the HURDAT2 dataset file (text format).

    Returns:
        A DataFrame containing hurricanes infomation that made landfall
        in Florida since 1900, with columns

    Raises:
        ValueError: If any line in the file does not match expected format.
        FileNotFoundError: If the file cannot be located.
    """ 
    florida_hurricanes = []
    huricane_name = None  
     
    with open(file) as f:
        lines = f.readlines()
        print(lines[1])

    for line in lines: 
        if line.startswith("AL"):
            info = [i.strip() for i in line.split(",")]
            if len(info) < 2:
                raise ValueError("Invalid input provided.")
            if len(info[0]) < 8:
                raise ValueError("Invalid hurricane format.")
            huricane_name = info[1]
        else:
            info = [i.strip() for i in line.split(",")]
            
            if len(info) < 21:
                raise ValueError("Invalid hurricane info format.")
            
            if info[2] == "L" and info[3] == "HU":
                month_year_date = info[0]
                year = int(month_year_date[0:4])
                month = int(month_year_date[4:6])
                day = int(month_year_date[6:8])
                
                time = info[1]
                hour = int(time[0:2])
                minute = int(time[2:4])
                
                if year < 1900:
                    continue
                
                lat_str = info[4]
                lat = float(lat_str[:-1]) * (1 if lat_str.endswith("N") else -1)
                lon_str = info[5]
                lon = float(lon_str[:-1]) * (-1 if lon_str.endswith("W") else 1)
                wind = int(info[6])
            
                if is_in_florida(lat, lon):
                    florida_hurricanes.append({
                        "name": huricane_name,
                        "year": year,
                        "month": month,
                        "day": day,
                        "time": f"{hour:02d}:{minute:02d}",
                        "wind": wind,
                    })
                    
    return pd.DataFrame(florida_hurricanes)

def parse_hurdat2_without_L_indicator(file):
    """
    Expanded version of parse_hurdat2 to find the huricanes that made landfall in Florida without using L indicator from the data file.
    Detect using the `global_land_mask` library
    """ 
    florida_hurricanes = []
    huricane_name = None  
    
    prev_on_land = False
    has_prev_point = False
     
    with open(file) as f:
        lines = f.readlines()
        print(lines[1])

    for line in lines: 
        if line.startswith("AL"):
            info = [i.strip() for i in line.split(",")]
            
            huricane_name = info[1]
            prev_on_land = False
            has_prev_point = False
        else:
            info = [i.strip() for i in line.split(",")]
             
            if info[3] == "HU":
                month_year_date = info[0]
                year = int(month_year_date[0:4])
                month = int(month_year_date[4:6])
                day = int(month_year_date[6:8])
                
                time = info[1]
                hour = int(time[0:2])
                minute = int(time[2:4])
                
                if year < 1900:
                    continue
                
                lat_str = info[4]
                lon_str = info[5]
                lat = float(lat_str[:-1]) * (1 if lat_str.endswith("N") else -1)
                lon = float(lon_str[:-1]) * (-1 if lon_str.endswith("W") else 1)
                
                wind = int(info[6])
                
                curr_on_land = not globe.is_ocean(lat, lon)

                if curr_on_land and not prev_on_land and has_prev_point:
                    if is_in_florida(lat, lon):
                        florida_hurricanes.append({
                            "name": huricane_name,
                            "year": year,
                            "month": month,
                            "day": day,
                            "time": f"{hour:02d}:{minute:02d}",
                            "wind": wind,
                        })

                prev_on_land = curr_on_land
                has_prev_point = True
                    
    return pd.DataFrame(florida_hurricanes)

@app.route("/")
def home():
    return "API is running."

@app.route("/export_csv", methods=["POST"])
def export_csv():
    """
    Export the Florida landfall hurricanes data to a CSV file.
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({
                "success": False,
                "code": 400,
                "error": "Request body must be a JSON list of objects."
            }), 400

        df = pd.DataFrame(data)
        export_path = DEFAULT_EXPORT_PATH 
        df.to_csv(export_path, index=False)

        return jsonify({
            "success": True,
            "code": 200,
            "message": f"CSV exported successfully to {export_path}",
            "rows": len(df)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "code": 500,
            "error": f"Internal server error: {e}"
        }), 500

@app.route("/hurricanes/landfall/florida", methods=["GET"])
def get_florida_landfall_hurricanes():
    """
    Get API endpoint to get hurricanes that made landfall in Florida.
    """
    try:
        df = parse_hurdat2(DATA_FILE)

        return jsonify({
            "success": True,
            "code": 200,
            "data": df.to_dict(orient="records")
        }), 200

    except FileNotFoundError as e:
        return jsonify({
            "success": False,
            "code": 404,
            "error": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "code": 500,
            "error": f"Internal server error: {e}"
        }), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
