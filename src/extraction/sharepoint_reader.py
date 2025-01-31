from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.files.file import File
import io

from config.settings import SHAREPOINT_SITE, CLIENT_ID, CLIENT_SECRET

def get_pdf_files():
    """Fetch PDF files directly from SharePoint (Microsoft Teams) without downloading."""
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(ClientCredential(CLIENT_ID, CLIENT_SECRET))
    library = ctx.web.get_folder_by_server_relative_url("/Shared Documents/Invoices").files
    ctx.load(library)
    ctx.execute_query()

    pdf_files = []
    for file in library:
        if file.name.endswith(".pdf"):
            response = File.open_binary(ctx, file.serverRelativeUrl)
            pdf_stream = io.BytesIO(response.content)
            pdf_files.append((file.name, pdf_stream))

    return pdf_files
