from distutils.command.build import build
import sys
import json
import requests
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLineEdit, QToolButton, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPalette, QColor

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.relativiti_api = RelativityApi()
        self.path_edit = None
        self.select_btn = None
        self.download_btn = None
        self.upload_btn = None
        self.init_window()
    
    def build_layout(self):
        # Main layout contain 2 layout
        layout = QVBoxLayout()
        # Layout1 for select path and button select
        layout1 = QHBoxLayout()
        # layout2 for upload and download button
        layout2 = QHBoxLayout()

        self.path_edit = QLineEdit(placeholderText='Select path folder to upload...')
        self.select_btn = QToolButton(text='...')
        # Layout2 for two button is download and upload
        self.download_btn = QPushButton("Download files")
        self.upload_btn = QPushButton("Upload files")

        layout1.addWidget(self.path_edit)
        layout1.addWidget(self.select_btn)
        self.select_btn.clicked.connect(self.select_folder)
        
        layout2.addWidget(self.upload_btn)
        layout2.addWidget(self.download_btn)
        self.upload_btn.clicked.connect(self.upload_files)
        self.download_btn.clicked.connect(self.download_files)
        
        #layout.addWidget(note_label, 20)
        
        layout.addLayout(layout1)
        layout.addLayout(layout2)

        return layout
    
    def init_window(self):
        self.setWindowTitle("Simple app to uplpad/download files via Relativity API")
        self.setFixedWidth(800)
        self.setFixedHeight(500)
        layout = self.build_layout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def select_folder(self):
        path_folder = QFileDialog.getExistingDirectory(None, "Select Folder")
        self.path_edit.setText(path_folder)
    
    def upload_files(self):
        pass

    def download_files(self):
        self.relativiti_api.donwload_files()
    

class RelativityApi(object):

    def __init__(self):
        self.relativity_path = "sgrelativity.deloittediscovery.com.sg"
        self.workspace_id = "1191625"
        self.bear_token = "QnJpYW4ubm9ycmllQGZhY3QzNjAuY286TWY1OWZoayE="
    

    def donwload_files(self):
        documents = self.get_collection_of_documents()
        if documents:
            # create folder output if not exist
            output = "output"
            if not os.path.isdir(output):
                os.mkdir(output)
            headers = self.build_headers()
            for document in documents:
                api_url = "https://{relativity_path}/Relativity.Rest/api/relativity-object-model/v1/workspaces/{workspace_id}/documents/{document_id}/native-file".format(
                    relativity_path=self.relativity_path,
                    workspace_id=self.workspace_id,
                    document_id=document['artifact_id']
                )
                print(api_url)
                try:
                    response = requests.get(api_url, headers=headers, allow_redirects=True)
                    print(response.status_code)
                    if response.status_code == 200:
                        with open(os.path.join(output, document['name']), 'wb') as f_write:
                            f_write.write(response.content)
                    else:
                        print("Error to download file" + document['name'])
                except Exception as e:
                    print("Error to download file" + document['name'] + ' - err ' + e)


    def build_headers(self):
        return {
            'X-CSRF-Header': '-',
            'Authorization': 'Basic ' + self.bear_token
        }
    
    def get_collection_of_documents(self):
        """
        Get collection of documents from specific workspace
        @Return a list of documents with pairs name and document_id
        """
        api_url = "https://{relativity_path}/Relativity.REST/Workspace/{workspace_id}/Document".format(relativity_path=self.relativity_path, workspace_id=self.workspace_id)
        headers = self.build_headers()
        response = self.call_api(api_url, headers, 'get')
        documents = []
        if response:
            for document in response['Results']:
                documents.append(
                    {
                        'name': document['Relativity Text Identifier'],
                        'artifact_id': document['Artifact ID']
                    }
                )
        else:
            print("Failed to get collection of documents")
        return documents

    def call_api(self, api_url, headers, method='get', body=None):
        try:
            if method == 'get':
                response = requests.get(api_url, headers=headers, json=body)
            elif method == 'post':
                response = requests.post(api_url, headers=headers, json=body)
            else:
                print("No method support!")
            if response.status_code == 200:
                return json.loads(response.content)
            else:
                print("Failed to call api with status code " + response.status_code)
        except Exception as e:
            print("Error to call API - err " + str(e))
        return None                                                                     


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()