"""Generate PDF proposal for Quick Scan Pro actions in the CrowdStrike OAuth SOAR connector."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime

OUTPUT = "/home/brian/soar/crowdstrikeoauth/QSP_Action_Proposal.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    leftMargin=0.85*inch,
    rightMargin=0.85*inch,
    topMargin=0.9*inch,
    bottomMargin=0.9*inch,
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle("Title", parent=styles["Title"],
    fontSize=22, spaceAfter=6, textColor=colors.HexColor("#CC0000"), leading=26)

subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
    fontSize=11, spaceAfter=16, textColor=colors.HexColor("#555555"), alignment=TA_CENTER)

h1 = ParagraphStyle("H1", parent=styles["Heading1"],
    fontSize=14, spaceBefore=18, spaceAfter=6,
    textColor=colors.HexColor("#CC0000"), borderPad=2)

h2 = ParagraphStyle("H2", parent=styles["Heading2"],
    fontSize=12, spaceBefore=12, spaceAfter=4,
    textColor=colors.HexColor("#333333"))

h3 = ParagraphStyle("H3", parent=styles["Heading3"],
    fontSize=10, spaceBefore=8, spaceAfter=3,
    textColor=colors.HexColor("#555555"), fontName="Helvetica-Bold")

body = ParagraphStyle("Body", parent=styles["Normal"],
    fontSize=9, leading=14, spaceAfter=4)

bullet = ParagraphStyle("Bullet", parent=styles["Normal"],
    fontSize=9, leading=13, leftIndent=16, spaceAfter=2,
    bulletIndent=6)

code_style = ParagraphStyle("Code", parent=styles["Code"],
    fontSize=7.5, leading=11, fontName="Courier",
    backColor=colors.HexColor("#F4F4F4"),
    leftIndent=10, rightIndent=10,
    borderColor=colors.HexColor("#DDDDDD"),
    borderWidth=0.5, borderPad=6,
    spaceAfter=6, spaceBefore=4)

note_style = ParagraphStyle("Note", parent=styles["Normal"],
    fontSize=8.5, leading=13, leftIndent=10,
    backColor=colors.HexColor("#FFF8E1"),
    borderColor=colors.HexColor("#F0C040"),
    borderWidth=0.5, borderPad=6,
    spaceAfter=6)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=6, spaceBefore=4)

def code(text):
    return Preformatted(text, code_style)

def p(text, style=body):
    return Paragraph(text, style)

def b(text):
    return Paragraph(f"• {text}", bullet)

story = []

# ── Title Page ──────────────────────────────────────────────────────────────
story.append(Spacer(1, 0.4*inch))
story.append(Paragraph("CrowdStrike OAuth SOAR Connector", title_style))
story.append(Paragraph("Proposed Changes: Quick Scan Pro Actions", subtitle_style))
story.append(Spacer(1, 0.1*inch))
story.append(hr())
story.append(Spacer(1, 0.1*inch))

meta_data = [
    ["Document Type:", "Engineering Proposal"],
    ["Connector:", "crowdstrikeoauthapi (v5.1.2)"],
    ["Feature:", "Quick Scan Pro API Integration"],
    ["Date:", datetime.date.today().strftime("%B %d, %Y")],
    ["Sources:", "FalconPy Documentation, Splunk SOAR SDK Reference"],
]
meta_table = Table(meta_data, colWidths=[1.4*inch, 4.5*inch])
meta_table.setStyle(TableStyle([
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTNAME", (1,0), (1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#555555")),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("TOPPADDING", (0,0), (-1,-1), 3),
]))
story.append(meta_table)
story.append(Spacer(1, 0.2*inch))
story.append(hr())

# ── 1. Overview ─────────────────────────────────────────────────────────────
story.append(p("1. Overview", h1))
story.append(p(
    "The CrowdStrike Quick Scan Pro API provides ML-based file scanning via the "
    "<b>/quickscanpro/</b> endpoint family. This proposal adds four new SOAR actions "
    "to the existing CrowdStrike OAuth connector, covering the full scan workflow: "
    "upload a file, launch a scan, retrieve results, and query scan history."
))
story.append(p(
    "The implementation follows the same patterns established by the existing "
    "FalconX Sandbox actions (<i>detonate_file</i>, <i>check_detonate_status</i>) "
    "and uses the connector's existing OAuth2 infrastructure (<b>_make_rest_call_helper_oauth2</b>)."
))

# ── 2. API Operations ────────────────────────────────────────────────────────
story.append(p("2. Quick Scan Pro API Operations", h1))
story.append(p("The following table maps each API operation to the proposed SOAR action:"))
story.append(Spacer(1, 0.05*inch))

api_table_data = [
    ["API Operation ID", "Method", "Endpoint", "Proposed SOAR Action"],
    ["UploadFileQuickScanPro", "POST", "/quickscanpro/entities/files/v1", "quick scan pro upload file"],
    ["LaunchScan", "POST", "/quickscanpro/entities/scans/v1", "quick scan pro launch scan"],
    ["GetScanResult", "GET", "/quickscanpro/entities/scans/v1", "quick scan pro get scan result"],
    ["QueryScanResults", "GET", "/quickscanpro/queries/scans/v1", "quick scan pro query scans"],
    ["DeleteFile", "DELETE", "/quickscanpro/entities/files/v1", "(deferred — future release)"],
    ["DeleteScanResult", "DELETE", "/quickscanpro/entities/scans/v1", "(deferred — future release)"],
]
api_table = Table(api_table_data, colWidths=[1.6*inch, 0.6*inch, 2.6*inch, 2.0*inch])
api_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#CC0000")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#CCCCCC")),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("TEXTCOLOR", (3,5), (3,6), colors.HexColor("#999999")),
    ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
    ("FONTNAME", (3,1), (3,4), "Helvetica-BoldOblique"),
]))
story.append(api_table)
story.append(Spacer(1, 0.1*inch))

# ── 3. Files to Modify ───────────────────────────────────────────────────────
story.append(p("3. Files to Modify", h1))

files_data = [
    ["File", "Change Type", "Description"],
    ["crowdstrikeoauthapi_consts.py", "Add constants", "Endpoint paths and status messages for Quick Scan Pro"],
    ["crowdstrikeoauthapi_connector.py", "Add methods", "4 handler methods + 4 entries in action_mapping dict"],
    ["crowdstrikeoauthapi.json", "Add actions", "4 action definitions with parameters and output data paths"],
    ["crowdstrike_qsp_upload_file.html", "New file", "Django template for upload file action result rendering"],
    ["crowdstrike_qsp_launch_scan.html", "New file", "Django template for launch scan action result rendering"],
    ["crowdstrike_qsp_get_scan_result.html", "New file", "Django template for get scan result rendering"],
    ["crowdstrike_qsp_query_scans.html", "New file", "Django template for query scans result rendering"],
    ["release_notes/unreleased.md", "Update", "Document new actions in release notes"],
]
files_table = Table(files_data, colWidths=[2.3*inch, 1.1*inch, 3.4*inch])
files_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#444444")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#CCCCCC")),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
    ("FONTNAME", (1,1), (1,-1), "Helvetica-Oblique"),
]))
story.append(files_table)

# ── 4. Constants ─────────────────────────────────────────────────────────────
story.append(p("4. Changes to crowdstrikeoauthapi_consts.py", h1))
story.append(p("Add the following constants at the end of the existing endpoint block:"))
story.append(code(
"""# Quick Scan Pro endpoints
CROWDSTRIKE_QSP_UPLOAD_FILE_ENDPOINT  = "/quickscanpro/entities/files/v1"
CROWDSTRIKE_QSP_LAUNCH_SCAN_ENDPOINT  = "/quickscanpro/entities/scans/v1"
CROWDSTRIKE_QSP_GET_SCAN_ENDPOINT     = "/quickscanpro/entities/scans/v1"
CROWDSTRIKE_QSP_QUERY_SCANS_ENDPOINT  = "/quickscanpro/queries/scans/v1"

# Quick Scan Pro status messages
CROWDSTRIKE_QSP_FILE_UPLOADED  = "File uploaded successfully to Quick Scan Pro"
CROWDSTRIKE_QSP_SCAN_LAUNCHED  = "Quick Scan Pro scan launched successfully"
CROWDSTRIKE_QSP_SCAN_NOT_FOUND = "No Quick Scan Pro scan results found for the given IDs"
"""
))

# ── 5. Connector Methods ─────────────────────────────────────────────────────
story.append(p("5. New Handler Methods in crowdstrikeoauthapi_connector.py", h1))
story.append(p(
    "Add the following four methods before the <b>handle_action</b> method (~line 5085). "
    "Each follows the same structure as existing handlers."
))

story.append(p("5.1  _handle_qsp_upload_file", h2))
story.append(p(
    "Reads a vault file by <b>vault_id</b> and POSTs it as <b>multipart/form-data</b> to the "
    "Quick Scan Pro files endpoint. The optional <b>scan</b> boolean triggers an immediate scan "
    "after upload. Returns the file's <b>sha256</b> in the summary for use in the next step. "
    "Uses <b>upload_file=True</b> to force a fresh OAuth token, consistent with "
    "<i>_handle_upload_put_file</i>."
))
story.append(code(
"""def _handle_qsp_upload_file(self, param):
    self.save_progress(f"In action handler for: {self.get_action_identifier()}")
    action_result = self.add_action_result(ActionResult(dict(param)))

    try:
        vault_id = param["vault_id"]
        _, _, file_info = phantom_rules.vault_info(vault_id=vault_id)
        file_info = next(iter(file_info))
    except Exception as e:
        return action_result.set_status(
            phantom.APP_ERROR,
            f"Vault ID not valid: {self._get_error_message_from_exception(e)}",
        )

    multipart_data = MultipartEncoder(
        fields={
            "file": (file_info["name"], open(file_info["path"], "rb")),
            "scan": str(param.get("scan", False)).lower(),
        }
    )
    headers = {"Content-Type": multipart_data.content_type}

    ret_val, resp_json = self._make_rest_call_helper_oauth2(
        action_result,
        CROWDSTRIKE_QSP_UPLOAD_FILE_ENDPOINT,
        headers=headers,
        data=multipart_data,
        method="post",
        upload_file=True,
    )

    if phantom.is_fail(ret_val):
        return action_result.get_status()

    action_result.add_data(resp_json)
    try:
        sha256 = resp_json["resources"][0]["sha256"]
        action_result.update_summary({"sha256": sha256})
    except (KeyError, IndexError):
        pass

    return action_result.set_status(phantom.APP_SUCCESS, CROWDSTRIKE_QSP_FILE_UPLOADED)
"""
))

story.append(p("5.2  _handle_qsp_launch_scan", h2))
story.append(p(
    "Accepts a <b>sha256</b> hash (returned by the upload action) and POSTs a scan request. "
    "Returns the <b>scan_id</b> in the summary for polling with get_scan_result."
))
story.append(code(
"""def _handle_qsp_launch_scan(self, param):
    self.save_progress(f"In action handler for: {self.get_action_identifier()}")
    action_result = self.add_action_result(ActionResult(dict(param)))

    json_payload = {"resources": [{"sha256": param["sha256"]}]}

    ret_val, resp_json = self._make_rest_call_helper_oauth2(
        action_result,
        CROWDSTRIKE_QSP_LAUNCH_SCAN_ENDPOINT,
        json_data=json_payload,
        method="post",
    )

    if phantom.is_fail(ret_val):
        return action_result.get_status()

    action_result.add_data(resp_json)
    try:
        scan_id = resp_json["resources"][0]["id"]
        action_result.update_summary({"scan_id": scan_id})
    except (KeyError, IndexError):
        pass

    return action_result.set_status(phantom.APP_SUCCESS, CROWDSTRIKE_QSP_SCAN_LAUNCHED)
"""
))

story.append(p("5.3  _handle_qsp_get_scan_result", h2))
story.append(p(
    "Retrieves results for one or more scan jobs by <b>scan_id</b> (comma-separated). "
    "Each resource is added as a separate data item. Returns the count of results in the summary."
))
story.append(code(
"""def _handle_qsp_get_scan_result(self, param):
    self.save_progress(f"In action handler for: {self.get_action_identifier()}")
    action_result = self.add_action_result(ActionResult(dict(param)))

    scan_ids = [s.strip() for s in param["scan_id"].split(",") if s.strip()]

    ret_val, resp_json = self._make_rest_call_helper_oauth2(
        action_result,
        CROWDSTRIKE_QSP_GET_SCAN_ENDPOINT,
        params={"ids": scan_ids},
        method="get",
    )

    if phantom.is_fail(ret_val):
        return action_result.get_status()

    resources = resp_json.get("resources", [])
    if not resources:
        return action_result.set_status(phantom.APP_SUCCESS, CROWDSTRIKE_QSP_SCAN_NOT_FOUND)

    for resource in resources:
        action_result.add_data(resource)

    action_result.update_summary({"scan_results_returned": len(resources)})
    return action_result.set_status(phantom.APP_SUCCESS)
"""
))

story.append(p("5.4  _handle_qsp_query_scans", h2))
story.append(p(
    "Queries scan job IDs using an optional FQL filter with offset/limit/sort pagination. "
    "Consistent with other <i>list_*</i> / <i>query_*</i> actions in the connector. "
    "Limit is capped at 5000 per the API maximum."
))
story.append(code(
"""def _handle_qsp_query_scans(self, param):
    self.save_progress(f"In action handler for: {self.get_action_identifier()}")
    action_result = self.add_action_result(ActionResult(dict(param)))

    params = {}
    if param.get("filter"):
        params["filter"] = param["filter"]
    if param.get("offset"):
        params["offset"] = param["offset"]
    if param.get("limit"):
        limit = self._validate_integers(action_result, param["limit"], "limit")
        if limit is None:
            return action_result.get_status()
        params["limit"] = min(limit, 5000)
    if param.get("sort"):
        params["sort"] = param["sort"]

    ret_val, resp_json = self._make_rest_call_helper_oauth2(
        action_result,
        CROWDSTRIKE_QSP_QUERY_SCANS_ENDPOINT,
        params=params,
        method="get",
    )

    if phantom.is_fail(ret_val):
        return action_result.get_status()

    scan_ids = resp_json.get("resources", [])
    for scan_id in scan_ids:
        action_result.add_data({"scan_id": scan_id})

    action_result.update_summary({"total_scans": len(scan_ids)})
    return action_result.set_status(phantom.APP_SUCCESS)
"""
))

# ── 6. handle_action ─────────────────────────────────────────────────────────
story.append(p("5.5  handle_action — action_mapping additions", h2))
story.append(p("Add these four entries to the <b>action_mapping</b> dict in <b>handle_action</b>:"))
story.append(code(
"""# In handle_action(), add to action_mapping dict:
"qsp_upload_file":     self._handle_qsp_upload_file,
"qsp_launch_scan":     self._handle_qsp_launch_scan,
"qsp_get_scan_result": self._handle_qsp_get_scan_result,
"qsp_query_scans":     self._handle_qsp_query_scans,
"""
))

# ── 6. App JSON ──────────────────────────────────────────────────────────────
story.append(p("6. New Action Definitions in crowdstrikeoauthapi.json", h1))
story.append(p("Add the following four entries to the <b>\"actions\"</b> array."))

story.append(p("6.1  quick scan pro upload file", h2))
story.append(code(
"""{
  "action": "quick scan pro upload file",
  "identifier": "qsp_upload_file",
  "description": "Uploads a file to Quick Scan Pro for ML-based scanning. Samples expire after 90 days.",
  "type": "generic",
  "read_only": false,
  "versions": "EQ(*)",
  "parameters": {
    "vault_id": {
      "description": "Vault ID of the file to upload",
      "data_type": "string",
      "required": true,
      "primary": true,
      "contains": ["vault id"],
      "order": 0
    },
    "scan": {
      "description": "Start scanning immediately after upload",
      "data_type": "boolean",
      "default": false,
      "order": 1
    }
  },
  "output": [
    { "data_path": "action_result.summary.sha256",       "data_type": "string", "contains": ["sha256"] },
    { "data_path": "action_result.data.*.sha256",        "data_type": "string", "contains": ["sha256"],
      "column_name": "SHA256", "column_order": 0 },
    { "data_path": "action_result.data.*.name",          "data_type": "string",
      "column_name": "File Name", "column_order": 1 },
    { "data_path": "action_result.status",               "data_type": "string" },
    { "data_path": "action_result.message",              "data_type": "string" }
  ],
  "render": { "type": "table", "title": "Quick Scan Pro Upload File", "width": 12, "height": 4 }
}
"""
))

story.append(p("6.2  quick scan pro launch scan", h2))
story.append(code(
"""{
  "action": "quick scan pro launch scan",
  "identifier": "qsp_launch_scan",
  "description": "Launches a Quick Scan Pro scan for a previously uploaded file identified by SHA256.",
  "type": "investigate",
  "read_only": false,
  "versions": "EQ(*)",
  "parameters": {
    "sha256": {
      "description": "SHA256 of the file to scan (returned by upload action)",
      "data_type": "string",
      "required": true,
      "primary": true,
      "contains": ["hash", "sha256"],
      "order": 0
    }
  },
  "output": [
    { "data_path": "action_result.summary.scan_id",     "data_type": "string" },
    { "data_path": "action_result.data.*.id",           "data_type": "string",
      "column_name": "Scan ID", "column_order": 0 },
    { "data_path": "action_result.data.*.status",       "data_type": "string",
      "column_name": "Status", "column_order": 1 },
    { "data_path": "action_result.status",              "data_type": "string" },
    { "data_path": "action_result.message",             "data_type": "string" }
  ],
  "render": { "type": "table", "title": "Quick Scan Pro Launch Scan", "width": 12, "height": 4 }
}
"""
))

story.append(p("6.3  quick scan pro get scan result", h2))
story.append(code(
"""{
  "action": "quick scan pro get scan result",
  "identifier": "qsp_get_scan_result",
  "description": "Retrieves the result of one or more Quick Scan Pro scans by scan job ID.",
  "type": "investigate",
  "read_only": true,
  "versions": "EQ(*)",
  "parameters": {
    "scan_id": {
      "description": "Scan job ID(s) to retrieve results for (comma-separated)",
      "data_type": "string",
      "required": true,
      "primary": true,
      "order": 0
    }
  },
  "output": [
    { "data_path": "action_result.summary.scan_results_returned", "data_type": "numeric" },
    { "data_path": "action_result.data.*.id",                     "data_type": "string",
      "column_name": "Scan ID", "column_order": 0 },
    { "data_path": "action_result.data.*.status",                 "data_type": "string",
      "column_name": "Status", "column_order": 1 },
    { "data_path": "action_result.data.*.result.verdict",         "data_type": "string",
      "column_name": "Verdict", "column_order": 2 },
    { "data_path": "action_result.data.*.result.threat_score",    "data_type": "numeric",
      "column_name": "Threat Score", "column_order": 3 },
    { "data_path": "action_result.data.*.sha256",                 "data_type": "string",
      "contains": ["sha256"], "column_name": "SHA256", "column_order": 4 },
    { "data_path": "action_result.status",                        "data_type": "string" },
    { "data_path": "action_result.message",                       "data_type": "string" }
  ],
  "render": { "type": "table", "title": "Quick Scan Pro Scan Result", "width": 12, "height": 5 }
}
"""
))

story.append(p("6.4  quick scan pro query scans", h2))
story.append(code(
"""{
  "action": "quick scan pro query scans",
  "identifier": "qsp_query_scans",
  "description": "Queries Quick Scan Pro scan job IDs using an optional FQL filter.",
  "type": "investigate",
  "read_only": true,
  "versions": "EQ(*)",
  "parameters": {
    "filter": {
      "description": "FQL filter (e.g. sha256:'<hash>'). Leave blank to return all recent scans.",
      "data_type": "string",
      "order": 0
    },
    "limit": {
      "description": "Maximum number of scan IDs to return (max 5000)",
      "data_type": "numeric",
      "default": 100,
      "order": 1
    },
    "offset": {
      "description": "Starting offset for pagination",
      "data_type": "numeric",
      "order": 2
    },
    "sort": {
      "description": "Sort order for results",
      "data_type": "string",
      "value_list": ["created_timestamp.asc", "created_timestamp.desc"],
      "default": "created_timestamp.desc",
      "order": 3
    }
  },
  "output": [
    { "data_path": "action_result.summary.total_scans",  "data_type": "numeric" },
    { "data_path": "action_result.data.*.scan_id",       "data_type": "string",
      "column_name": "Scan ID", "column_order": 0 },
    { "data_path": "action_result.status",               "data_type": "string" },
    { "data_path": "action_result.message",              "data_type": "string" }
  ],
  "render": { "type": "table", "title": "Quick Scan Pro Query Scans", "width": 12, "height": 5 }
}
"""
))

# ── 7. Design Decisions ───────────────────────────────────────────────────────
story.append(p("7. Design Decisions", h1))

decisions = [
    ("<b>Follows FalconX pattern.</b> The upload → sha256 → launch scan → get result workflow "
     "mirrors the existing FalconX detonation flow (upload_file → _submit_resource_for_detonation → "
     "check_detonate_status). Analysts familiar with FalconX actions will find Quick Scan Pro intuitive."),

    ("<b>upload_file=True on the upload call.</b> Forces a fresh OAuth token, consistent with "
     "_handle_upload_put_file and the existing _upload_file helper. Required because file upload "
     "endpoints reject stale tokens."),

    ("<b>Comma-separated scan_id in get_scan_result.</b> Follows how ids are handled elsewhere "
     "in the connector (e.g., _handle_get_detections_details) and allows bulk result retrieval "
     "in a single SOAR action execution."),

    ("<b>No DeleteFile / DeleteScanResult in this release.</b> Destructive cleanup operations "
     "are lower priority. They can be added in a follow-on without any architectural changes "
     "since all infrastructure will already be in place."),

    ("<b>No new asset configuration required.</b> Quick Scan Pro uses the same OAuth2 client "
     "credentials and base URL already configured in the connector asset. No user-facing "
     "configuration changes are needed."),

    ("<b>Limit capped at 5000 in qsp_query_scans.</b> Per the API documentation maximum. "
     "Uses the existing _validate_integers helper for input validation, consistent with "
     "other paginated list actions."),
]
for d in decisions:
    story.append(KeepTogether([p(f"• {d}", bullet), Spacer(1, 0.04*inch)]))

# ── 8. Testing ────────────────────────────────────────────────────────────────
story.append(p("8. Testing Approach", h1))
story.append(p("Test each action using the connector's standard standalone test JSON pattern:"))
story.append(code(
"""{
  "asset_id": "1",
  "connector_run_id": 1,
  "action": "quick scan pro upload file",
  "identifier": "qsp_upload_file",
  "parameters": [{"vault_id": "<vault_id>", "scan": false}],
  "debug_level": 3,
  "config": {
    "url": "https://api.crowdstrike.com",
    "client_id": "<client_id>",
    "client_secret": "<client_secret>"
  },
  "environment_variables": {}
}
"""
))
story.append(p("Run with:"))
story.append(code(
"""export PYTHONPATH=/opt/phantom/lib/:/opt/phantom/www/
export REQUESTS_CA_BUNDLE=/opt/phantom/etc/cacerts.pem
phenv python3 crowdstrikeoauthapi_connector.py /tmp/test_qsp_upload.json
"""
))
story.append(p("The complete test sequence is:"))
story.append(b("Upload a file → capture sha256 from summary"))
story.append(b("Launch scan with sha256 → capture scan_id from summary"))
story.append(b("Poll get_scan_result with scan_id until status is 'done'"))
story.append(b("Verify verdict and threat_score fields are present in result data"))
story.append(b("Run query_scans with filter=sha256:'&lt;hash&gt;' to confirm scan appears in history"))

# ── Footer ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 0.3*inch))
story.append(hr())
story.append(p(
    f"Generated {datetime.date.today().strftime('%B %d, %Y')} · "
    "CrowdStrike OAuth SOAR Connector · Quick Scan Pro Proposal",
    ParagraphStyle("footer", parent=styles["Normal"], fontSize=7.5,
                   textColor=colors.HexColor("#999999"), alignment=TA_CENTER)
))

doc.build(story)
print(f"PDF written to {OUTPUT}")
