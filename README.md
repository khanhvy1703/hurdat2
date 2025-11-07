# Florida Hurricane Landfall Since 1900
- Backend: Python 3.11+, Flask
- Frontend: React/Nextjs + Typescript and ChakraUI for styling

## Server Overview:
#### Server Functions
1. **is_in_florida**: check if the given latitude and longitude falls within bounding box of the state of Florida
2. **parse_hurdat2**: use NOAA’s “L” Landfall Indicator to detect events marked as landfall from the data file.  
3. **parse_hurdat2_without_L_indicator**: detect landfall without the “L” Indicator.
#### Landfall Detection Logic: 
- Check the prev lat/lon points whether or not they are on the ocean, then check the current lat/lon endpoint whether or not they are on land. 
- Check make sure all points are inside Florida boundary box
- Use `global_land_mask` library to check if a coordinate is on land or ocean.
- Consider it is landfall if the current lat/lon cord is on land while the prev lat/lon cord in the ocean. 
- If the next lat/lon cord also on land we dont consider it.
#### Server API Endpoints
1. **GET `/`**: health check
2. **GET `/hurricanes/landfall/florida`**: returns a list of all hurricanes that made landfall in Florida since 1900, the api currently uses the `parse_hurdat2` function
3. **POST `/export_csv`** : accepts list of hurricane records as json data and exports it to a CSV file, the exported file is saved inside the server folder

## Dashboard Overview
The dashboard is built with React and Next.js and styled using Chakra UI for component styling. It has:

- A table view of all Florida landfall hurricanes since 1900 showing the name of the storm, date, time, and max wind  
- Filters to view hurricanes by time period:
    - All periods
    - 1900–1949  
    - 1950–1999  
    - 2000–2050  
- CSV export button to save and export the filtered data.   
- Basic loading and error states for data fetching.

## Setup locally
Clone the repo: 
```bash
git clone https://github.com/khanhvy1703/hurdat2.git

cd hurdat2
```
### Server
``` bash
cd server

# Install Dependencies
pip install Flask flask-cors pandas global-land-mask
# Run the server locally
python app.py
```
Once it starts successfully, you should see something like this:
```
Running on http://localhost:5000
```

### Dashboard
Inside the dashboard folder. Create `.env` file in the main root of the dashboard folder 
```
NEXT_PUBLIC_SERVER_ENDPOINT = http://localhost:5000
```
Then run
``` bash 
# To build the project
npm run build
# then to start the project
npm run start

# or 
npm run dev # to run it in dev enviorment
```
