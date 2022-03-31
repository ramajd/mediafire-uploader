import os
import pprint
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from mediafire import MediaFireApi, MediaFireUploader


class UploaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.api = MediaFireApi()
        self.session = None
        self.uploader = None

    def initUI(self):
        self.setWindowTitle("MediaFire Uploader")
        self.resize(640, 480)

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        upload_layout = QHBoxLayout()

        self.txtEmail = QLineEdit()
        form_layout.addRow("Email", self.txtEmail)

        self.txtPassword = QLineEdit()
        self.txtPassword.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password", self.txtPassword)

        self.txtAppID = QLineEdit()
        form_layout.addRow("App ID", self.txtAppID)

        self.txtUploadUrl = QLineEdit()
        self.txtUploadUrl.setReadOnly(True)
        upload_layout.addWidget(self.txtUploadUrl)

        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_for_file)
        upload_layout.addWidget(btn_browse)
        form_layout.addRow("Select file to upload", upload_layout)
        main_layout.addLayout(form_layout)

        btn_upload = QPushButton("Upload")
        btn_upload.clicked.connect(self.upload)
        btn_upload.setEnabled(False)
        main_layout.addWidget(btn_upload)

        def upload_url_status_handler():
            enabled = True
            if len(self.txtEmail.text()) == 0 \
                    or len(self.txtPassword.text()) == 0 \
                    or len(self.txtAppID.text()) == 0 \
                    or len(self.txtUploadUrl.text()) == 0:
                enabled = False
            btn_upload.setEnabled(enabled)
        self.txtEmail.textChanged.connect(upload_url_status_handler)
        self.txtPassword.textChanged.connect(upload_url_status_handler)
        self.txtAppID.textChanged.connect(upload_url_status_handler)
        self.txtUploadUrl.textChanged.connect(upload_url_status_handler)

        self.txtResult = QTextEdit()
        self.txtResult.setReadOnly(True)
        main_layout.addWidget(self.txtResult)

        self.setLayout(main_layout)
        self.sizeHint()
        self.show()
        btn_browse.setFocus()

    def browse_for_file(self):
        self.txtUploadUrl.setText('')
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select file to upload", "", "All Files (*)", options=options)
        if file_name:
            self.txtUploadUrl.setText(file_name)

    def set_result(self, msg_type, message):
        self.txtResult.setStyleSheet(
            "color: 'red'" if msg_type == 'error' else '')
        self.txtResult.setText(message)

    def login(self, email, password, appid):
        session = self.api.user_get_session_token(
            email=email,
            password=password,
            app_id=appid)
        return session

    def upload(self):
        self.setEnabled(False)
        self.set_result("", "uploading ...")
        self.repaint()
        try:
            if not self.session or not self.uploader:
                email = self.txtEmail.text()
                password = self.txtPassword.text()
                app_id = self.txtAppID.text()
                self.session = self.login(email, password, app_id)
                if not self.session:
                    raise Exception('Upload failed')

                self.api.session = self.session
                user = self.api.user_get_info()
                print('> logged in as: {}'.format(
                    user['user_info']['display_name']))
                self.uploader = MediaFireUploader(self.api)
            upload_path = self.txtUploadUrl.text()
            print('> upload new file: {}'.format(upload_path))
            with open(upload_path, 'rb') as fd:
                upload_result = self.uploader.upload(
                    fd, os.path.basename(upload_path))
                details = self.api.file_get_info(upload_result.quickkey)
                self.set_result('success', pprint.pformat(
                    details, indent=2))
        except Exception as err:
            print('> upload failed: {}'.format(str(err)))
            self.set_result('error', str(err))
        finally:
            self.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = UploaderApp()
    # a.txtEmail.setText("my.email@gmail.com")
    # a.txtPassword.setText("123456789")
    # Change APP_ID to provided value from MediaFire developer dashboard
    a.txtAppID.setText("42511")
    app.exec()
