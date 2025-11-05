import pandas as pd

FLORIDA_BOUNDS = {
    "lat_min": 24.45,
    "lat_max": 31.00,
    "lon_min": -87.63,
    "lon_max": -80.03
}

def is_in_florida(lat, lon):
    """
    Check if coordinates fall within Florida’s bounding box.
    """
    return (FLORIDA_BOUNDS["lat_min"] <= lat <= FLORIDA_BOUNDS["lat_max"] and
            FLORIDA_BOUNDS["lon_min"] <= lon <= FLORIDA_BOUNDS["lon_max"])

def parse_hurdat2(filepath):
    """
    Parse the HURDAT2 text file and extract hurricane landfalls in Florida.
    """ 
    florida_hurricanes = []
    huricane_name = None  
     
    with open(filepath) as f:
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
            
            if len(info) < 6:
                raise ValueError("Invalid input provided.")
            
            if info[2] == "L" and info[3] == "HU":
                month_year_date = info[0]
                year = int(month_year_date[0:4])
                month = int(month_year_date[4:6])
                day = int(month_year_date[6:8])
                
                if year >= 1900:
                    lat_str = info[4]
                    lat = float(lat_str[:-1]) * (1 if lat_str.endswith("N") else -1)
                    lon_str = info[5]
                    lon = float(lon_str[:-1]) * (-1 if lon_str.endswith("W") else 1)
                
                    if is_in_florida(lat, lon):
                        florida_hurricanes.append({
                            "name": huricane_name,
                            "year": year,
                            "month": month,
                            "day": day,
                            "latitude": lat,
                            "longitude": lon,
                        })
                    
    return pd.DataFrame(florida_hurricanes)

def main():
    """Run the analysis and save the report."""
    df = parse_hurdat2("hurdat2-1851-2024-040425.txt")
    df.to_csv("florida_hurricane_landfalls.csv", index=False)

if __name__ == "__main__":
    main()