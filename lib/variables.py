new_device_column_set_id = 120
#sll_verify = False
sll_verify = lib_base_path+"kamu.ca-bundle"
api_base_url = "https://xxx.com/api/v1/"
update_base_url = "https://xxx.com/uploads/mesaiTakipCihazi/"
get_device_key_url_path = "mesaiTakipCihaziAnahtarGetir"
device_table_name = "mesai_takip_cihazlar"

try:
	from localVariables import * 
except Exception as e:
	rfid_read_mode_async = True
	same_rfid_read_control = True
	relay_only_true_user = False 