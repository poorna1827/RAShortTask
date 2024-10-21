import sys
# Append the path to the module to sys.path
module_path = r"C:\wt\mini_wt\tws-api\source\pythonclient"
sys.path.insert(0, module_path)

# Now you can import the ibapi module
import ibapi

# Verify the module's file location
print(ibapi.__file__)
from ibapi.server_versions import *
print("Version:", ibapi.VERSION)

