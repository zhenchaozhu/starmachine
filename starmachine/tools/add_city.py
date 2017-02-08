# coding: utf-8

import xlrd
from starmachine.model.country import Country
from starmachine.model.province import Province
from starmachine.model.city import City
from starmachine.model.district import District

file_path = 'areaid_list.xlsx'
data = xlrd.open_workbook(file_path)

table = data.sheets()[0]
nrows = table.nrows

for i in range(1, nrows):
    row_data = table.row_values(i)
    country_name = row_data[8]
    country_name_en = row_data[7]
    province_name = row_data[6]
    province_en = row_data[5]
    city_name = row_data[4]
    city_en = row_data[3]
    district_name = row_data[2]
    district_en = row_data[1]

    country = Country.get_by_name(country_name)
    if not country:
        country = Country.add(country_name, country_name_en)

    province = Province.get_by_name(province_name)
    if not province:
        province = Province.add(country.id, province_name, province_en)

    city = City.get_by_name(city_name)
    if not city:
        city = City.add(province.id, city_name, city_en)

    district = District.get_by_name(district_name)
    if not district:
        district = District.add(city.id, district_name, district_en)


