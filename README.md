# Heatwaves
Heatwave detection in Estonian Environment Agency daily max temperature data, following their definition:
   - every day exceeding fixed or day specific threshold is a heat day.
   - at least 3 heat days in a row is a heatwave.
   - if one day is cooler than threshold but the previous and next day both
     meet the threshold then the heatwave continues.

Assumes the following columns in the input daily maximum temperature xlsx file table: Aasta, Kuu, Paev, followed by any N of station columns.

# Usage
The script is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. USE AT YOUR OWN RISK!
