"""
Build a ChromaDB vector database from Splunk SOAR app development documentation.
"""
import chromadb
from sentence_transformers import SentenceTransformer
import json

# Initialize ChromaDB (persistent)
client = chromadb.PersistentClient(path="/home/brian/soar/soar_docs_db")
collection = client.get_or_create_collection(
    name="soar_app_dev_docs",
    metadata={"hnsw:space": "cosine"}
)

model = SentenceTransformer("all-MiniLM-L6-v2")

docs = [
    {
        "id": "arch_overview",
        "topic": "App Architecture Overview",
        "text": """A Splunk SOAR app consists of two primary interfaces:
1. External interface — interacts with external devices or services (REST APIs, SDKs, etc.)
2. Platform interface — communicates with Splunk SOAR to execute actions, report progress, and return results

The app is packaged as a TAR file containing:
- A JSON manifest file (e.g., myapp.json) — defines metadata, actions, config
- A Python connector module (e.g., myapp_connector.py) — implements logic
- An __init__.py file (enables local module imports)
- Optional: view files, constants files, wheels/dependencies

BaseConnector is the main point of contact between the app connector class and the Splunk SOAR platform.
Your connector class extends it:

    import phantom.app as phantom
    from phantom.base_connector import BaseConnector
    from phantom.action_result import ActionResult

    class MyAppConnector(BaseConnector):
        def __init__(self):
            super(MyAppConnector, self).__init__()
            self._state = None
            self._base_url = None
"""
    },
    {
        "id": "action_result",
        "topic": "ActionResult",
        "text": """ActionResult abstracts the result representation for a single action execution.
Each call to handle_action should create one ActionResult:

    def _handle_some_action(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        # ... do work ...
        action_result.add_data(response_dict)
        action_result.update_summary({"key": "value"})
        return action_result.set_status(phantom.APP_SUCCESS)

ActionResult JSON structure:
{
   "parameter": {"domain": "amazon.com"},
   "status": "success",
   "message": "Query successful",
   "summary": {"city": "Reno", "country": "US"},
   "data": [{"contacts": {...}, "nameservers": [...]}]
}

ActionResult methods:
- add_data(item): Adds dict to data list
- update_data(item): Extends data list
- get_data(): Returns current data list
- add_debug_data(item): Adds debug info shown on failure
- set_status(status_code, message, exception): Sets action result status
- get_status(): Returns phantom.APP_SUCCESS or phantom.APP_ERROR
- is_success() / is_fail(): Boolean status checks
- get_message(): Returns message string
- update_summary(summary): Updates summary dict; returns the summary dict
- get_summary(): Returns current summary
"""
    },
    {
        "id": "add_new_action",
        "topic": "Adding New Actions to an Existing SOAR App",
        "text": """To add a new action to an existing SOAR app:

STEP 1 — Add the action to the JSON manifest (myapp.json) in the "actions" array:
{
  "action": "geolocate ip",
  "identifier": "geolocate_ip",
  "description": "Queries service for IP location information",
  "type": "investigate",
  "read_only": true,
  "versions": "EQ(*)",
  "parameters": {
    "ip": {
      "description": "IP to geolocate",
      "data_type": "string",
      "required": true,
      "primary": true,
      "contains": ["ip"],
      "order": 0
    }
  },
  "output": [
    {"data_path": "action_result.data.*.ip", "data_type": "string", "contains": ["ip"], "column_name": "IP", "column_order": 0},
    {"data_path": "action_result.data.*.country", "data_type": "string", "column_name": "Country", "column_order": 1},
    {"data_path": "action_result.status", "data_type": "string"},
    {"data_path": "action_result.message", "data_type": "string"}
  ],
  "render": {"type": "table", "title": "Geolocate IP", "width": 6, "height": 4}
}

STEP 2 — Add the handler method to the connector:
    def _handle_geolocate_ip(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        ip = param['ip']
        ret_val, response = self._make_rest_call("/ip/{0}".format(ip), action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()
        action_result.add_data(response)
        summary = action_result.update_summary({})
        summary['coordinates'] = response.get("loc")
        return action_result.set_status(phantom.APP_SUCCESS)

STEP 3 — Register it in handle_action:
    def handle_action(self, param):
        action_id = self.get_action_identifier()
        if action_id == "geolocate_ip":
            return self._handle_geolocate_ip(param)
        elif action_id == "on_poll":
            return self._handle_on_poll(param)
        # etc.
"""
    },
    {
        "id": "handle_action_dispatch",
        "topic": "handle_action Method and Action Dispatch Pattern",
        "text": """When a user runs an action, the platform:
1. Gathers asset config and action info into an Action JSON
2. Calls BaseConnector._handle_action(action_json_str, handle)
3. _handle_action validates configuration variables
4. Calls AppConnector.initialize() — if error, skips action processing
5. For each entry in the parameters array, calls AppConnector.handle_action(param_dict)
6. Calls AppConnector.finalize()
7. Generates and returns the connector run result JSON

The Action JSON fed to _handle_action:
{
   "config": {"whois_server": "whois.arin.net"},
   "identifier": "whois_domain",
   "parameters": [{"domain": "amazon.com"}, {"domain": "google.com"}]
}

Typical handle_action dispatcher:
    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS
        action_id = self.get_action_identifier()
        self.debug_print("action_id", self.get_action_identifier())

        if action_id == "test_asset_connectivity":
            ret_val = self._handle_test_connectivity(param)
        elif action_id == "list_incidents":
            ret_val = self._handle_list_incidents(param)
        elif action_id == "on_poll":
            ret_val = self._handle_on_poll(param)
        return ret_val
"""
    },
    {
        "id": "asset_config_params",
        "topic": "Asset Configuration and Action Parameters",
        "text": """Asset configuration defines static parameters set once per asset (credentials, URLs, etc.)
in the JSON manifest under "configuration":

"configuration": {
  "base_url": {
    "data_type": "string",
    "description": "The Base URL to connect to",
    "required": true,
    "default": "https://api.example.com",
    "order": 0
  },
  "api_key": {"data_type": "password", "description": "API Key", "required": true, "order": 1},
  "verify_ssl": {"data_type": "boolean", "description": "Verify SSL certificates", "default": true, "order": 2},
  "timeout": {"data_type": "numeric", "description": "Request timeout in seconds", "default": 30, "order": 3}
}

Supported data_type values: string, password (masked in UI), numeric, boolean, file, ph (placeholder)

Accessing config in Python:
    def initialize(self):
        self._state = self.load_state()
        config = self.get_config()
        self._base_url = config['base_url']
        self._api_key = config.get('api_key')
        return phantom.APP_SUCCESS

Action parameter keys:
- description: UI display text (required)
- data_type: string, password, numeric, boolean (required)
- contains: data classification tags for playbook chaining e.g. ["ip"], ["hash"]
- required: whether mandatory
- primary: primary subject of the action
- value_list: predefined dropdown choices
- default: default value
- order: display order (0-based)
- allow_list: support comma-separated multiple values
"""
    },
    {
        "id": "rest_calls",
        "topic": "Making REST Calls Within a Connector",
        "text": """Standard _make_rest_call pattern using requests library:

    class RetVal(tuple):
        def __new__(cls, val1, val2=None):
            return tuple.__new__(RetVal, (val1, val2))

    def _process_response(self, r, action_result):
        action_result.add_debug_data({'response_status_code': r.status_code})
        action_result.add_debug_data({'response_text': r.text})
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR,
                "Unable to parse JSON response. Error: {0}".format(str(e))), None)
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)
        error_text = resp_json.get('message', r.text)
        return RetVal(action_result.set_status(phantom.APP_ERROR,
            "Error from server. Status: {0}. Message: {1}".format(r.status_code, error_text)), resp_json)

    def _make_rest_call(self, endpoint, action_result, method="get", **kwargs):
        config = self.get_config()
        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(action_result.set_status(phantom.APP_ERROR,
                "Invalid method: {0}".format(method)), None)
        url = self._base_url + endpoint
        try:
            r = request_func(url, verify=config.get('verify_server_cert', False), **kwargs)
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR,
                "Error Connecting to server. Details: {0}".format(str(e))), None)
        return self._process_response(r, action_result)

Using _make_rest_call in an action handler:
    def _handle_lookup_ip(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        ip = param['ip']
        ret_val, response = self._make_rest_call('/ip/{0}'.format(ip), action_result,
            method="get", headers={'Authorization': 'Bearer {0}'.format(self._api_key)})
        if phantom.is_fail(ret_val):
            return action_result.get_status()
        action_result.add_data(response)
        return action_result.set_status(phantom.APP_SUCCESS)

CA Bundle note: At runtime, Splunk SOAR sets REQUESTS_CA_BUNDLE to /opt/phantom/etc/cacerts.pem.
Also available via BaseConnector.get_ca_bundle().
"""
    },
    {
        "id": "state_management",
        "topic": "State Management: load_state and save_state",
        "text": """State management is critical for polling connectors that need to remember position across runs.

BaseConnector state methods:
- load_state(): Loads state file into dict. Creates with app_version field if not exists. Returns the state dict.
- save_state(state_dict): Writes dict to a persistent state file.
- get_state(): Returns current state dict or None.
- get_state_file_path(): Returns full path to state file.

Standard pattern:
    def initialize(self):
        self._state = self.load_state()
        if not isinstance(self._state, dict):
            self._state = {}
        config = self.get_config()
        self._base_url = config['base_url']
        return phantom.APP_SUCCESS

    def finalize(self):
        self.save_state(self._state)
        return phantom.APP_SUCCESS

Tracking poll position:
    def _handle_on_poll(self, param):
        if self._state.get('first_run', True):
            self._state['first_run'] = False
            last_time = (datetime.now() - timedelta(days=7)).isoformat()
        else:
            last_time = self._state.get('last_ingested_time',
                (datetime.now() - timedelta(days=1)).isoformat())
        # ... ingest data ...
        self._state['last_ingested_time'] = datetime.now().isoformat()
        self.save_state(self._state)

Storing tokens in state:
    def _generate_new_access_token(self, action_result):
        # ... make auth call ...
        self._state[STATE_TOKEN_KEY] = resp_json['access_token']
        self.save_state(self._state)
        return phantom.APP_SUCCESS
"""
    },
    {
        "id": "ingestion_on_poll",
        "topic": "Container and Artifact Creation During Ingestion (on_poll)",
        "text": """on_poll action JSON definition:
{
  "action": "on poll",
  "identifier": "on_poll",
  "description": "Ingest events from the service",
  "type": "ingest",
  "read_only": true,
  "parameters": {
    "start_time": {"data_type": "numeric", "description": "Start of time range in epoch time (ms)"},
    "end_time": {"data_type": "numeric"},
    "container_id": {"data_type": "string"},
    "container_count": {"data_type": "numeric"},
    "artifact_count": {"data_type": "numeric"}
  },
  "output": []
}

Artifact structure:
{
  "name": "Artifact Name",
  "label": "event",
  "source_data_identifier": "unique-id-from-source",
  "severity": "medium",
  "cef": {
    "sourceAddress": "192.168.1.1",
    "destinationPort": 443,
    "fileHash": "abc123"
  },
  "cef_types": {
    "sourceAddress": ["ip"],
    "fileHash": ["md5"]
  },
  "data": {"raw": "original data"},
  "run_automation": false
}

Key artifact fields:
- name: Human-readable artifact name
- label: Classification (event, FWAlert, incident, etc.)
- source_data_identifier: SDI from source — critical for deduplication
- severity: low, medium, high, critical
- cef: Normalized Common Event Format fields
- cef_types: Maps CEF fields to data types for playbook chaining
- run_automation: Set True only on the last artifact — triggers active playbooks once per container

Container save:
    container = {
        'name': 'Incident Title',
        'source_data_identifier': 'incident-unique-id',
        'severity': 'medium',
        'status': 'new',
        'artifacts': [artifact1, artifact2]
    }
    status, message, container_id = self.save_container(container)

Save methods:
- save_artifact(artifact): (status, message, id)
- save_artifacts(artifacts): (status, message, id_list)
- save_container(container): (status, message, container_id) — preferred, saves container + artifacts in one call
- save_containers(containers): bulk, most performant

Vault operations:
    from phantom.vault import Vault
    success, message, vault_id = vault.vault_add(container=container_id,
        file_location='/tmp/myfile.pdf', file_name='report.pdf')
    resp = Vault.create_attachment(file_contents_bytes, container_id, file_name='data.json')
    tmp_dir = Vault.get_vault_tmp_dir()

is_poll_now(): Returns True if triggered by Poll Now button (use for first-run vs scheduled logic).
"""
    },
    {
        "id": "app_json_schema",
        "topic": "App JSON Manifest Schema",
        "text": """Top-level required fields in the app JSON manifest:
- appid: UUID v4 — unique app identifier
- name: App display name
- description: Verbose app overview
- type: Category: siem, email, endpoint, firewall, reputation, ticketing, network, etc.
- main_module: Filename of the Python module entry point (e.g., myapp_connector.py)
- app_version: Version string (e.g., 1.0.0)
- product_vendor: Third-party vendor name
- product_name: Supported product name
- product_version_regex: Regex for supported product versions (e.g., .*)
- publisher: Creator or organization
- package_name: Installation package identifier
- license: License string
- python_version: Must be "3"
- configuration: Asset configuration variables dict
- actions: Array of action definitions

Action type values:
- test: Asset connectivity validation
- investigate: Read-only lookups
- contain: Blocking/containment actions
- correct: Remediation actions
- generic: General-purpose
- ingest: Data ingestion (on_poll)

Output data path format:
- action_result.data.*.field_name — field from raw API response data list
- action_result.data.*.nested.field — nested field
- action_result.summary.field_name — summary field
- action_result.status — success/failure
- action_result.message — status message
- action_result.parameter.param_name — echo of input parameter

Render configuration:
"render": {
  "type": "table",       // "json", "table", or "custom"
  "title": "Results",
  "width": 6,            // 1-6 (use 12 for investigation actions)
  "height": 4,           // 0-10
  "view": "myapp_view.function_name",  // for type "custom"
  "menu_name": "My App Lookup"
}

Pip dependencies:
"pip_dependencies": {
  "pypi": [{"module": "requests"}, {"module": "cryptography==41.0.1"}],
  "wheel": [{"module": "python-rtkit", "input_file": "wheels/python_rtkit-0.7.0-py27-none-any.whl"}]
}

Action locking (serialization):
"lock": {"enabled": true, "data_path": "parameters.ip", "timeout": 600}
"""
    },
    {
        "id": "baseconnector_api",
        "topic": "BaseConnector API Reference",
        "text": """BaseConnector lifecycle methods:
- initialize(): Called before action processing; return phantom.APP_SUCCESS or APP_ERROR
- finalize(): Called after all parameters processed; summarize and cleanup
- handle_action(param): Required. Main action dispatch; called once per param dict entry
- handle_cancel(): Called when action is cancelled
- handle_exception(exception): Called on unhandled exception

Action/Config methods:
- get_action_identifier(): Returns current action identifier string
- get_current_param(): Returns active parameter dictionary
- get_config(): Returns connector run configuration dict
- get_app_config(): Returns app configuration dict
- get_app_json(): Returns complete app JSON as dict

Result management:
- add_action_result(action_result): Adds ActionResult to connector run; returns the object
- get_action_results(): Returns list of all ActionResult objects
- set_status(status_code, message, exception): Sets connector run status
- get_status(): Returns current connector status
- update_summary(summary): Updates connector run summary dict

Progress/Debug:
- save_progress(msg): Sends persistent progress message (saved to storage, visible in UI)
- send_progress(msg): Sends transient progress message (overwritten by next call)
- debug_print(tag, dump_object): Dumps formatted debug output to spawn.log
- error_print(tag, dump_object): Logs ERROR-level messages

Container/Asset info:
- get_container_id(): Returns current container ID
- get_asset_id(): Returns current asset ID
- get_app_id() / get_connector_id(): Returns app identifier
- get_container_info(container_id): Returns container details
- get_product_version(): Returns Splunk SOAR version
- is_poll_now(): Returns True if triggered by Poll Now button
- get_ca_bundle(): Returns path to CA bundle

phantom module constants:
- phantom.APP_SUCCESS  # True
- phantom.APP_ERROR    # False
- phantom.is_success(ret_val)
- phantom.is_fail(ret_val)
- phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY  # "test_asset_connectivity"
- phantom.APP_JSON_CONTAINER_COUNT           # "container_count"
"""
    },
    {
        "id": "testing",
        "topic": "Testing SOAR Apps",
        "text": """Standalone testing with a JSON input file:

Create test JSON (e.g., /tmp/test_action.json):
{
  "asset_id": "4",
  "connector_run_id": 2,
  "action": "geolocate ip",
  "identifier": "geolocate_ip",
  "parameters": [{"ip": "8.8.8.8"}],
  "debug_level": 3,
  "config": {
    "base_url": "https://ipinfo.io",
    "verify_server_cert": false
  },
  "environment_variables": {}
}

Set environment and run:
    export PYTHONPATH=/opt/phantom/lib/:/opt/phantom/www/
    export REQUESTS_CA_BUNDLE=/opt/phantom/etc/cacerts.pem
    phenv python3 myapp_connector.py /tmp/test_action.json

Standard __main__ block in connector:
    if __name__ == '__main__':
        import argparse, pudb
        pudb.set_trace()
        argparser = argparse.ArgumentParser()
        argparser.add_argument('input_test_json', help='Input Test JSON file')
        args = argparser.parse_args()
        with open(args.input_test_json) as f:
            in_json = json.loads(f.read())
        connector = MyAppConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

Unit testing with pytest-splunk-soar-connectors:
    pip install pytest-splunk-soar-connectors

    # tests/conftest.py
    pytest_plugins = ("splunk-soar-connectors",)

    # tests/test_myapp.py
    from pytest_splunk_soar_connectors import configure_connector
    def test_lookup_ip():
        connector = configure_connector(MyAppConnector, {"base_url": "...", "api_key": "..."})
        result_str = connector._handle_action(json.dumps({
            "action": "lookup ip", "identifier": "lookup_ip",
            "config": {}, "parameters": [{"ip": "8.8.8.8"}], "environment_variables": {}
        }), None)
        result = json.loads(result_str)
        assert result[0]["status"] == "success"

Compile and install on SOAR platform:
    phenv compile_app -i
"""
    },
    {
        "id": "crowdstrike_connector_specifics",
        "topic": "CrowdStrike OAuth SOAR Connector — Specific Patterns",
        "text": """The CrowdStrike OAuth connector (crowdstrikeoauthapi_connector.py) uses these patterns:

OAuth2 token management:
- Tokens stored encrypted in state file per tenant (multi-tenant via subtenants CIDs config)
- Token refreshed every ~29 minutes via a background interval
- decrypt_state() / finalize() handle encrypt/decrypt using encryption_helper module
- _oauth_access_token is a dict keyed by tenant CID

Key connector attributes initialized in initialize():
- self._base_url_oauth: CrowdStrike API base URL (e.g., https://api.crowdstrike.com)
- self._client_id / self._client_secret: OAuth2 credentials from asset config
- self._headers: {"Content-Type": "application/json"}
- self._state: loaded from load_state()
- self._asset_id: from get_asset_id()
- self._parameters: {"appId": app_id} — sent with streaming API calls

Streaming ingestion (on_poll):
- Uses /sensors/entities/datafeed/v2 endpoint
- Parses DetectionSummaryEvent and EppDetectionSummaryEvent types
- parse_cs_events.py converts raw events to SOAR containers/artifacts
- parse_cs_incidents.py handles incident ingestion
- State tracks last feed offset to avoid duplicates
- DEFAULT_EVENTS_COUNT = 10000, DEFAULT_POLLNOW_EVENTS_COUNT = 2000

RetVal pattern used throughout:
    class RetVal(tuple):
        def __new__(cls, val1, val2):
            return tuple.__new__(RetVal, (val1, val2))

All constants (endpoint paths, config keys, error messages) are in crowdstrikeoauthapi_consts.py
and imported with: from crowdstrikeoauthapi_consts import *

All API endpoint path constants are named CROWDSTRIKE_*_ENDPOINT, e.g.:
- CROWDSTRIKE_OAUTH_TOKEN_ENDPOINT = "/oauth2/token"
- CROWDSTRIKE_LIST_DETECTIONS_ENDPOINT = "/detects/queries/detects/v1"
- CROWDSTRIKE_LIST_DETECTIONS_DETAILS_ENDPOINT = "/detects/entities/summaries/GET/v1"

Success HTTP status codes: CROWDSTRIKE_API_SUCC_CODES = [200, 202, 204]

preprocess_script: asset config supports an optional Python script (exec'd) that must
define preprocess_container(container) — applied to containers before saving during ingestion.

HTML view files (*.html) use Django templates and correspond one-per-action.
crowdstrike_view.py provides custom render functions referenced in render.view of the JSON.
"""
    },
]

print(f"Encoding {len(docs)} documents...")
texts = [d["text"] for d in docs]
embeddings = model.encode(texts, show_progress_bar=True)

print("Adding to ChromaDB collection...")
collection.upsert(
    ids=[d["id"] for d in docs],
    embeddings=embeddings.tolist(),
    documents=[d["text"] for d in docs],
    metadatas=[{"topic": d["topic"], "id": d["id"]} for d in docs],
)

print(f"\nDone. Collection '{collection.name}' now has {collection.count()} documents.")
print("DB path: /home/brian/soar/soar_docs_db")

# Quick sanity-check query
print("\n--- Sanity check: query 'how to add a new action' ---")
query = "how to add a new action to a SOAR connector"
q_embedding = model.encode([query])[0]
results = collection.query(query_embeddings=[q_embedding.tolist()], n_results=3)
for i, (doc_id, meta, dist) in enumerate(zip(
    results["ids"][0], results["metadatas"][0], results["distances"][0]
)):
    print(f"  {i+1}. [{doc_id}] {meta['topic']} (distance: {dist:.4f})")
