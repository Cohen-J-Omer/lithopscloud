import http.client
import json
import requests

from config.config_tool.util_func import get_option_from_list, update_config_file, free_dialog, \
    _get_oauth_token, get_confirmation, get_resource_group_id

CF_REGIONS = ['eu-de', 'eu-gb', 'us-south', 'us-east', 'au-syd', 'jp-tok']


def config_cf():

    is_cf_based_namespace = False  # set to true if namespace is cloud foundry based
    print("\n\n Configuring IBM cloud functions:")

    create_new_namespace = get_confirmation("Would you like to create a new namespace and "
                                            "use it in the configuration?")['answer']
    if create_new_namespace:
        region = get_option_from_list('Please choose the region you would like to create a namespace in :'
                                      , CF_REGIONS)['answer']
        chosen_namespace = free_dialog("Please name your cloud foundry namespace: ")['answer']
        namespace_id = create_cloud_function_namespaces(region, chosen_namespace)

    else:  # user would like to use an already existing namespace
        region = get_option_from_list('Please choose the region your namespace resides in :', CF_REGIONS)['answer']
        cloud_namespaces = get_cloud_function_namespaces(region)
        chosen_namespace = get_option_from_list('Please choose a namespace :',
                                                list(cloud_namespaces.keys()))['answer']

        if cloud_namespaces[chosen_namespace]['type'] == 'CF_based':
            cf_api_key = free_dialog("Please provide your cloud foundry api_key from: "
                                     "https://cloud.ibm.com/functions/namespace-settings ")['answer']
            update_config_file(f"""ibm_cf:
                                    endpoint: https://{region}.functions.cloud.ibm.com
                                    namespace: {chosen_namespace}
                                    api_key: {cf_api_key}""")
            is_cf_based_namespace = True

        else:  # API_based namespace
            namespace_id = cloud_namespaces[chosen_namespace]['id']

    if not is_cf_based_namespace:  # a cf_based_namespace hasn't already been configured
        update_config_file(f"""ibm_cf:
                                endpoint: https://{region}.functions.cloud.ibm.com
                                namespace: {chosen_namespace}
                                namespace_id: {namespace_id}""")

    print("\n------IBM Cloud Function was configured successfully------\n")


def _get_cloud_function_namespaces_metadata(region):
    """returns meta data on namespaces of ibm cloud functions within a specified region """
    iam_token = _get_oauth_token()
    conn = http.client.HTTPSConnection(f"{region}.functions.cloud.ibm.com")
    conn.request("GET", "/api/v1/namespaces", headers={'Authorization': iam_token})
    res = conn.getresponse()
    metadata = res.read().decode("utf-8")
    json_struct = json.loads(metadata)  # turn string to a dictionary

    return json_struct


def get_cloud_function_namespaces(region):
    """returns the names of the namespaces with a given region"""
    namespaces = {}
    for name_space in _get_cloud_function_namespaces_metadata(region)['namespaces']:
        if 'name' in name_space:  # API based namespace
            namespaces[name_space['name']] = {'type': 'API_based', 'id': name_space['id']}
        else:  # cloud foundry based namespace
            namespaces[name_space['id']] = {'type': 'CF_based'}
    return namespaces


def create_cloud_function_namespaces(region, name):
    """creates a name space in a given region, under a specified resource group and returns the namespace id"""
    iam_token = _get_oauth_token()
    resource_group_id = get_resource_group_id()[0]
    headers = {'Authorization': iam_token, 'accept': 'application/json'}
    data = {"name": name, "resource_group_id": resource_group_id, "resource_plan_id": "functions-base-plan"}
    response = requests.post(f'https://{region}.functions.cloud.ibm.com/api/v1/namespaces',
                             headers=headers, json=data).json()
    return response['id']

