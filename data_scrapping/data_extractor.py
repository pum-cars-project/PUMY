IRRELEVANT_DATA_PARAMETERS = {"vin", "date_registration", "registration", "catalog_urn"}


def extract(json_data):
    root = json_data["props"]["pageProps"]["advert"]
    extracted_data = dict()
    extracted_data["id"] = root["id"]
    extract_parameters(root["parametersDict"], extracted_data)
    extract_price(root["price"], extracted_data)
    return extracted_data


def extract_price(price, formatted_data):
    formatted_data["price"] = {
        "amount": price["value"],
        "currency": price["currency"]
    }


def extract_parameters(parameters_data, formatted_data):
    relevant_parameters = [value for key, value in parameters_data.items() if key not in IRRELEVANT_DATA_PARAMETERS]
    for value in relevant_parameters:
        formatted_data[value["label"]] = parse_value(value["values"][0]["value"])


def parse_value(value):
    if value == "1" or value == "0":
        return bool(int(value))
    return value
