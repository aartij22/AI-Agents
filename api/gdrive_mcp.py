import os
import io
import re
from fastmcp import FastMCP
from rich.pretty import pprint
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload


def get_drive_service(client_secret_path):
    """
    To get the client_secret json, follow the steps mentioned under getting started and Authentication here -
    https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive
    Args:
        client_secret_path: Path to client_secret.json
    Returns:
        Google Drive service client
    """
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("../token.json", "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def get_file_id_from_url(url: str) -> str:
    """
    Google API requires file_id's to share docs.
    Args:
        url: Google Drive link to extract the file_id from
    Returns:
        file ID from the url
    """
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    raise ValueError("Could not extract file ID from the URL")


mcp = FastMCP("gdrive")
gdrive_service = get_drive_service(client_secret_path='')


@mcp.tool()
def create_google_doc(session_id: str, title: str, content, folder_id: str = None) -> dict:
    """
    Create a new Google Docs document with the specified title and content.

    Args:
        title: The title of the Google Docs document to create.
        content: The textual content to insert into the document.
        folder_id: The ID of the Google Drive folder where the document should be created.

    Returns:
        The file ID of the newly created Google Docs document.
    """
    if isinstance(content, dict):
        content = content.get("text", "")
    file_metadata = {"name": title, "mimeType": "application/vnd.google-apps.document"}
    if folder_id:
        file_metadata["parents"] = [folder_id]  # This specifies the destination folder

    media = MediaIoBaseUpload(
        io.BytesIO(content.encode("utf-8")), mimetype="text/plain", resumable=False
    )

    file = (
        gdrive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"Created document: {title} with ID: {file.get('id')}")
    return {"file_id": file.get("id")}


@mcp.tool()
def share_google_doc(session_id: str, file_id: str, email: str, role: str = "writer") -> None:
    """
    Share a Google Doc file with a specified user by email with a given access role.

    Args:
        file_id: The ID of the Google Drive file to share.
        email: The email address of the user to share the file with.
        role: The access role to grant the user (e.g., 'reader', 'commenter', 'writer'). Defaults to 'writer'.

    Returns:
        Formatted string with success message.
    """
    permission = {"type": "user", "role": role, "emailAddress": email}
    gdrive_service.permissions().create(
        fileId=file_id, body=permission, sendNotificationEmail=True
    ).execute()
    return f"Shared with {email} as {role}"


@mcp.tool()
def read_google_doc(session_id: str, file_url: str) -> str:
    """
    Reads the content of a Google Docs or plain text file from Google Drive.

    Args:
        file_url (str): The URL of the Google Drive file.

    Returns:
        str: The content of the file as a UTF-8 decoded string.

    Raises:
        ValueError: If the file's MIME type is unsupported.
        HttpError: If an error occurs during the API request.
    """
    file_id = get_file_id_from_url(file_url)

    try:
        # Retrieve the MIME type of the file
        file_metadata = (
            gdrive_service.files().get(fileId=file_id, fields="mimeType").execute()
        )
        mime_type = file_metadata.get("mimeType")

        # Determine the appropriate request based on MIME type
        if mime_type == "application/vnd.google-apps.document":
            request = gdrive_service.files().export(
                fileId=file_id, mimeType="text/plain"
            )
        elif mime_type == "text/plain":
            request = gdrive_service.files().get_media(fileId=file_id)
        else:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

        # Download the file content
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        content_bytes = fh.read()
        return content_bytes.decode("utf-8") if content_bytes else None

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


if __name__ == "__main__":
    mcp.run(transport="sse", port=3002)
