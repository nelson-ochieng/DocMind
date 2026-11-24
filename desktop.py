"""DocMind 4.2 native desktop interface. All inference is performed locally by Ollama."""
from __future__ import annotations
import html
import re
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem, QTextEdit,
    QLineEdit, QStackedWidget, QMessageBox, QFrame, QSplitter, QProgressBar,
    QComboBox, QCheckBox, QScrollArea, QTextBrowser, QDialog, QInputDialog
)
import config
from modules.llm import ollama_status
from modules.document_processor import extract_document, document_id
from modules.chunker import chunk_document
from modules.vector_store import VectorStore
from modules.rag_engine import RAGEngine
from modules.chat_manager import ChatManager

LIGHT = '''
QWidget {background:#F7F8FC;color:#20263B;font-family:'Segoe UI';font-size:14px}
QFrame#panel {background:#FFFFFF;border:1px solid #E6E9F0;border-radius:16px}
QPushButton {background:#ECEFFA;border:0;border-radius:10px;padding:11px 16px;font-weight:600}
QPushButton:hover {background:#DDE5FF}
QPushButton#primary {background:#4657DB;color:white}
QPushButton#primary:hover {background:#3346C6}
QPushButton:disabled {background:#E9EBF2;color:#9499A8}
QLineEdit,QTextEdit,QTextBrowser,QListWidget,QComboBox {background:white;border:1px solid #DDE2EC;border-radius:10px;padding:9px}
QListWidget::item {padding:10px;border-radius:8px}
QListWidget::item:selected {background:#E4E9FF;color:#222B68}
QLabel {background:transparent}
QScrollBar:horizontal {height:8px;background:transparent}
QScrollBar::handle:horizontal {background:#8993aa;border-radius:4px;min-width:25px}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {width:0px}
QPushButton#nav {text-align:left;padding:12px;background:transparent}
QPushButton#nav:hover {background:#64748b33}
QScrollBar:vertical {width:10px;background:transparent}
QScrollBar::handle:vertical {background:#8993aa;border-radius:5px;min-height:25px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0px}
QLabel#muted {color:#69738A}
QProgressBar {border:0;background:#E7EBF3;border-radius:5px;height:8px}
QProgressBar::chunk {background:#4657DB;border-radius:5px}
'''
DARK = '''
QWidget {background:#141925;color:#EDF1FF;font-family:'Segoe UI';font-size:14px}
QFrame#panel {background:#1D2535;border:1px solid #303A4E;border-radius:16px}
QPushButton {background:#303C57;color:#EDF1FF;border:0;border-radius:10px;padding:11px 16px;font-weight:600}
QPushButton:hover {background:#405073}
QPushButton#primary {background:#7888FF;color:#11182D}
QPushButton#primary:hover {background:#98A4FF}
QPushButton:disabled {background:#283044;color:#8590A7}
QLineEdit,QTextEdit,QTextBrowser,QListWidget,QComboBox {background:#202A3B;color:#EDF1FF;border:1px solid #39465D;border-radius:10px;padding:9px}
QListWidget::item {padding:10px;border-radius:8px}
QListWidget::item:selected {background:#3A4772;color:white}
QLabel {background:transparent}
QScrollBar:horizontal {height:8px;background:transparent}
QScrollBar::handle:horizontal {background:#8993aa;border-radius:4px;min-width:25px}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {width:0px}
QPushButton#nav {text-align:left;padding:12px;background:transparent}
QPushButton#nav:hover {background:#64748b33}
QScrollBar:vertical {width:10px;background:transparent}
QScrollBar::handle:vertical {background:#8993aa;border-radius:5px;min-height:25px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0px}
QLabel#muted {color:#A3B0C8}
QProgressBar {border:0;background:#303A4E;border-radius:5px;height:8px}
QProgressBar::chunk {background:#7888FF;border-radius:5px}
'''

class Job(QThread):
    completed = Signal(object)
    failed = Signal(str)
    def __init__(self, func):
        super().__init__()
        self.func = func
    def run(self):
        try:
            self.completed.emit(self.func())
        except Exception as exc:
            self.failed.emit(str(exc))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DocMind — Your private document assistant')
        self.resize(1320, 850)
        self.setMinimumSize(900, 620)
        self.store = None
        self.chats = ChatManager()
        self.conversation_id = None
        self.messages = []
        self.jobs = []
        self.operation_busy = False
        self.current_theme = 'Light'
        self.build_ui()
        self.apply_theme('Light')
        self.refresh_status()
        self.refresh_documents()
        self.new_chat()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(24,20,24,20)
        outer.setSpacing(14)
        top = QHBoxLayout()
        brand = QLabel('✦  DocMind')
        brand.setStyleSheet('font-size:26px;font-weight:800')
        top.addWidget(brand)
        top.addStretch()
        self.status = QLabel('Checking local AI…')
        self.status.setObjectName('muted')
        top.addWidget(self.status)
        self.theme = QComboBox()
        self.theme.addItems(['Light','Dark'])
        self.theme.currentTextChanged.connect(self.apply_theme)
        top.addWidget(self.theme)
        outer.addLayout(top)
        subtitle = QLabel('Your documents, explained simply. Private by design.')
        subtitle.setObjectName('muted')
        outer.addWidget(subtitle)
        body = QHBoxLayout()
        body.setSpacing(18)
        nav = QVBoxLayout()
        nav.setSpacing(10)
        for label, index in [('💬  Ask DocMind',0),('📚  My documents',1),('⚙  Setup & privacy',2)]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, i=index:self.navigate(i))
            b.setObjectName("nav")
            nav.addWidget(b)
        nav.addSpacing(10)
        nav.addWidget(QLabel('RECENT CONVERSATIONS'))
        self.history = QListWidget()
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history.setWordWrap(True)
        self.history.itemClicked.connect(self.open_chat)
        nav.addWidget(self.history, 1)
        new_btn = QPushButton('+ New conversation')
        new_btn.clicked.connect(self.new_chat)
        nav.addWidget(new_btn)
        nav_container = QFrame()
        nav_container.setObjectName('panel')
        nav_container.setFixedWidth(245)
        nav_container.setLayout(nav)
        nav.setContentsMargins(12,16,12,12)
        body.addWidget(nav_container)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.chat_page())
        self.stack.addWidget(self.documents_page())
        self.stack.addWidget(self.setup_page())
        body.addWidget(self.stack,1)
        outer.addLayout(body,1)
        self.busy_bar = QProgressBar()
        self.busy_bar.setRange(0,1)
        self.busy_bar.setValue(0)
        self.busy_bar.setVisible(False)
        outer.addWidget(self.busy_bar)
        self.notice = QLabel('All document processing stays on this computer. No cloud account required.')
        self.notice.setObjectName('muted')
        outer.addWidget(self.notice)

    def panel(self, layout):
        frame = QFrame()
        frame.setObjectName('panel')
        frame.setLayout(layout)
        layout.setContentsMargins(24,24,24,24)
        layout.setSpacing(13)
        return frame

    def chat_page(self):
        layout = QVBoxLayout()
        heading = QLabel('Ask your documents')
        heading.setStyleSheet('font-size:23px;font-weight:700')
        layout.addWidget(heading)
        hint = QLabel('Choose a document and ask a question. Sources are linked in every answer.')
        hint.setObjectName('muted')
        layout.addWidget(hint)
        quick = QHBoxLayout()
        for title, prompt in [('Summarize','Summarize the main points of my documents.'),('Explain simply','Explain the most important ideas in simple language.'),('Methodology','Analyse the research methodology in detail, including data, procedures and validation.'),('Compare','Compare the main points across the documents.')]:
            b = QPushButton(title)
            b.clicked.connect(lambda _,p=prompt:self.set_prompt(p))
            quick.addWidget(b)
        layout.addLayout(quick)
        scope = QHBoxLayout()
        self.scope = QComboBox()
        self.scope.addItem('All documents', None)
        scope.addWidget(self.scope,1)
        self.model = QComboBox()
        self.model.addItem(config.LLM_MODEL)
        scope.addWidget(self.model)
        add=QPushButton("+ Add files"); add.clicked.connect(self.add_documents); scope.addWidget(add)
        layout.addLayout(scope)
        self.transcript = QTextBrowser()
        self.transcript.setOpenLinks(False)
        self.transcript.anchorClicked.connect(self.open_source)
        self.transcript.setReadOnly(True)
        self.transcript.document().setDocumentMargin(24)
        self.transcript.setPlaceholderText('Your conversation will appear here.')
        layout.addWidget(self.transcript,1)
        inputrow = QHBoxLayout()
        self.question = QLineEdit()
        self.question.setPlaceholderText('Ask anything about your documents…')
        self.question.returnPressed.connect(self.ask)
        inputrow.addWidget(self.question,1)
        self.ask_button = QPushButton('Send ↑')
        self.ask_button.setObjectName('primary')
        self.ask_button.clicked.connect(self.ask)
        inputrow.addWidget(self.ask_button)
        layout.addLayout(inputrow)
        tools = QHBoxLayout()
        for label, kind in [('Flowchart','flow'),('Mind map','mind'),('Chart','chart')]:
            b=QPushButton(label); b.clicked.connect(lambda _,k=kind:self.visualize(k)); tools.addWidget(b)
        export = QPushButton('Export report')
        export.clicked.connect(self.export_chat)
        tools.addWidget(export)
        copy=QPushButton('Copy answer'); copy.clicked.connect(lambda: QApplication.clipboard().setText(next((m['content'] for m in reversed(self.messages) if m['role']=='assistant'),''))); tools.addWidget(copy)
        layout.addLayout(tools)
        return self.panel(layout)

    def documents_page(self):
        layout = QVBoxLayout()
        heading = QLabel('My documents')
        heading.setStyleSheet('font-size:23px;font-weight:700')
        layout.addWidget(heading)
        hint = QLabel('PDF, Word, or text files · Maximum 25 MB per file')
        hint.setObjectName('muted')
        layout.addWidget(hint)
        add = QPushButton('+ Add documents')
        add.setObjectName('primary')
        add.clicked.connect(self.add_documents)
        layout.addWidget(add,alignment=Qt.AlignmentFlag.AlignLeft)
        self.docs = QListWidget()
        self.docs.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.docs,1)
        row = QHBoxLayout()
        delete = QPushButton('Remove selected document')
        delete.clicked.connect(self.remove_document)
        row.addWidget(delete)
        row.addStretch()
        ask = QPushButton('Ask about my documents →')
        ask.clicked.connect(lambda:self.navigate(0))
        row.addWidget(ask)
        layout.addLayout(row)
        return self.panel(layout)

    def setup_page(self):
        layout = QVBoxLayout()
        heading = QLabel('Setup & privacy')
        heading.setStyleSheet('font-size:23px;font-weight:700')
        layout.addWidget(heading)
        info = QLabel('DocMind uses Ollama to run AI on your own computer. The first setup needs internet to download the models.')
        info.setWordWrap(True)
        layout.addWidget(info)
        self.setup_state = QLabel('Checking…')
        self.setup_state.setWordWrap(True)
        layout.addWidget(self.setup_state)
        row = QHBoxLayout()
        refresh = QPushButton('Check connection')
        refresh.clicked.connect(self.refresh_status)
        row.addWidget(refresh)
        website = QPushButton('Install Ollama')
        website.clicked.connect(lambda:QDesktopServices.openUrl(QUrl('https://ollama.com/download/windows')))
        row.addWidget(website)
        layout.addLayout(row)
        for name,model in [('Install chat model (about 2 GB)',config.LLM_MODEL),('Install document model',config.EMBEDDING_MODEL)]:
            button = QPushButton(name)
            button.clicked.connect(lambda _,m=model:self.pull_model(m))
            layout.addWidget(button,alignment=Qt.AlignmentFlag.AlignLeft)
        note = QLabel('If Ollama is installed but not running, open Ollama from the Start menu and click Check connection.')
        note.setObjectName('muted')
        note.setWordWrap(True)
        layout.addWidget(note)
        from modules.hardware import recommendation
        ram, suggested = recommendation()
        layout.addWidget(QLabel(f'RAM: {ram:.1f} GB · Suggested: {suggested}'))
        recommended=QPushButton('Install recommended model'); recommended.clicked.connect(lambda:self.pull_model(suggested)); layout.addWidget(recommended)
        layout.addSpacing(12)
        location = QLabel(f'Local data folder: {config.DATA_DIR}')
        location.setWordWrap(True)
        layout.addWidget(location)
        open_folder = QPushButton('Open my local data folder')
        open_folder.clicked.connect(lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(config.DATA_DIR))))
        layout.addWidget(open_folder,alignment=Qt.AlignmentFlag.AlignLeft)
        clear = QPushButton('Delete all local documents and conversations')
        clear.clicked.connect(self.clear_data)
        layout.addWidget(clear,alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        return self.panel(layout)

    def navigate(self,index):
        self.stack.setCurrentIndex(index)
        if index==1:self.refresh_documents()
        if index==2:self.refresh_status()

    def apply_theme(self,name):
        self.current_theme=name
        QApplication.instance().setStyleSheet(DARK if name=='Dark' else LIGHT)

    def run_job(self,func,success):
        if self.operation_busy:
            QMessageBox.information(self, 'Please wait', 'DocMind is finishing another task.')
            return
        self.operation_busy = True
        self.ask_button.setEnabled(False)
        self.busy_bar.setVisible(True)
        self.busy_bar.setRange(0,0)
        job=Job(func)
        self.jobs.append(job)
        def finish(result):
            self.finish_job(job)
            success(result)
        def fail(message):
            self.finish_job(job)
            self.notice.setText('Something went wrong: '+message)
            QMessageBox.warning(self,'DocMind needs attention',message)
        job.success_callback=finish
        job.failure_callback=fail
        job.completed.connect(self.job_success, Qt.ConnectionType.QueuedConnection)
        job.failed.connect(self.job_failure, Qt.ConnectionType.QueuedConnection)
        job.start()

    def job_success(self,result):
        job=self.sender(); job.wait(); job.success_callback(result)

    def job_failure(self,message):
        job=self.sender(); job.wait(); job.failure_callback(message)

    def finish_job(self,job):
        self.operation_busy = False
        self.ask_button.setEnabled(True)
        self.busy_bar.setRange(0,1)
        self.busy_bar.setValue(0)
        self.busy_bar.setVisible(False)
        if job in self.jobs:self.jobs.remove(job)
        job.deleteLater()

    def refresh_status(self):
        def check():
            return ollama_status()
        def done(result):
            ok,_,models=result
            from modules.hardware import recommendation
            ram, suggested = recommendation()
            self.model.clear()
            self.model.addItems([m for m in models if "embed" not in m] or [config.LLM_MODEL])
            self.model.setCurrentText(config.LLM_MODEL)
            self.setup_state.setToolTip(f"RAM: {ram:.1f} GB; suggested model: {suggested}")
            chat=any(x==config.LLM_MODEL or x.startswith(config.LLM_MODEL+'-') for x in models)
            embedding=any(x==config.EMBEDDING_MODEL or x.startswith(config.EMBEDDING_MODEL+':') for x in models)
            self.status.setText('● Local AI ready' if ok and chat and embedding else '● Setup needed')
            self.setup_state.setText(('Ollama connected. ' if ok else 'Ollama is not running. ') +
                ('Chat model ready. ' if chat else f'Chat model missing: {config.LLM_MODEL}. ') +
                ('Document model ready.' if embedding else f'Document model missing: {config.EMBEDDING_MODEL}.'))
        self.run_job(check,done)

    def pull_model(self,model):
        if not shutil.which('ollama'):
            QMessageBox.information(self,'Install Ollama','Install Ollama first, then restart DocMind.')
            return
        self.notice.setText(f'Downloading {model} locally. This may take several minutes…')
        def download():
            result=subprocess.run(['ollama','pull',model],capture_output=True,text=True,timeout=3600,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            if result.returncode:raise RuntimeError((result.stderr or result.stdout)[-700:])
            return model
        self.run_job(download,lambda _: (self.notice.setText('Model installed successfully.'),self.refresh_status()))

    def get_store(self):
        if self.store is None:self.store=VectorStore()
        return self.store

    def refresh_documents(self):
        self.docs.clear()
        self.scope.clear()
        self.scope.addItem("All documents",None)
        try:
            for filename,meta in sorted(self.get_store().list_documents().items()):
                item=QListWidgetItem(f'📄  {filename}    ·    {meta["chunks"]} passages')
                item.setData(Qt.ItemDataRole.UserRole,meta)
                self.docs.addItem(item)
                self.scope.addItem(filename,meta["document_id"])
        except Exception as exc:
            self.notice.setText('Document library could not be loaded: '+str(exc))

    def add_documents(self):
        paths,_=QFileDialog.getOpenFileNames(self,'Choose documents',str(Path.home()),'Documents (*.pdf *.docx *.txt)')
        if not paths:return
        self.notice.setText(f'Adding {len(paths)} document(s)…')
        def process():
            results=[]
            store=self.get_store()
            for raw in paths:
                source=Path(raw)
                if source.suffix.lower() not in config.SUPPORTED_EXTENSIONS:raise ValueError('Unsupported file format')
                if source.stat().st_size > config.MAX_UPLOAD_MB*1024*1024:raise ValueError(f'{source.name} exceeds 25 MB')
                from modules.document_processor import sanitize_filename
                safe=sanitize_filename(source.name)
                destination=config.DOCUMENTS_DIR/safe
                if destination.exists() and destination.resolve()!=source.resolve():
                    raise FileExistsError(f'A document named {safe} already exists. Rename it first.')
                if source.resolve()!=destination.resolve():
                    shutil.copy2(source,destination)
                did=document_id(destination)
                pages=extract_document(destination)
                chunks=chunk_document(destination,did,pages,config.CHUNK_SIZE,config.CHUNK_OVERLAP)
                if not chunks:
                    if source.resolve()!=destination.resolve():destination.unlink(missing_ok=True)
                    raise ValueError(f'No readable text found in {safe}. Scanned PDFs may require OCR.')
                store.replace_document(chunks)
                results.append(safe)
            return results
        self.run_job(process,lambda names:(self.refresh_documents(),self.notice.setText('Ready: '+', '.join(names))))

    def remove_document(self):
        item=self.docs.currentItem()
        if not item:return
        meta=item.data(Qt.ItemDataRole.UserRole)
        name=meta['source_filename']
        if QMessageBox.question(self,'Remove document',f'Remove {name} from your library and local storage?')!=QMessageBox.StandardButton.Yes:return
        def remove():
            self.get_store().delete_document(meta['document_id'])
            (config.DOCUMENTS_DIR/name).unlink(missing_ok=True)
            return name
        self.run_job(remove,lambda _:self.refresh_documents())

    def set_prompt(self,prompt):
        self.navigate(0)
        self.question.setText(prompt)
        self.question.setFocus()

    def new_chat(self):
        if self.operation_busy and self.conversation_id is not None:return
        self.conversation_id=self.chats.new_conversation()
        self.messages=[]
        self.render_chat()
        self.refresh_history()
        self.navigate(0)

    def refresh_history(self):
        self.history.clear()
        for convo in self.chats.list_conversations()[:40]:
            item=QListWidgetItem(convo['title'])
            item.setData(Qt.ItemDataRole.UserRole,convo['id'])
            self.history.addItem(item)

    def open_chat(self,item):
        if self.operation_busy:return
        self.conversation_id=item.data(Qt.ItemDataRole.UserRole)
        self.messages=self.chats.get_messages(self.conversation_id)
        self.render_chat()
        self.navigate(0)

    def render_chat(self):
        parts=[]
        self.source_links=[]
        for message in self.messages:
            role='You' if message['role']=='user' else 'DocMind'
            from modules.presentation import render
            links={}
            if message['role']=='assistant':
                for source in message.get('sources',[]):
                    cid=source.get('citation_id')
                    if f'[{cid}]' in message['content']:
                        links[cid]=len(self.source_links); self.source_links.append(source)
            content=render(message['content'],links) if role=='DocMind' else html.escape(message['content'])
            parts.append(f'<p style="font-size:12px;color:#818cf8"><b>{role}</b></p>{content}<hr>')
        self.transcript.setHtml(''.join(parts) if parts else '<p style="color:#8490A8">Add a document, then ask your first question.</p>')
        self.transcript.moveCursor(self.transcript.textCursor().MoveOperation.End)

    def ask(self):
        if self.operation_busy:return
        question=self.question.text().strip()
        if not question:return
        if self.get_store().count()==0:
            QMessageBox.information(self,'Add a document first','Open My documents and add a PDF, Word or text file.')
            self.navigate(1)
            return
        self.question.clear()
        self.chats.add_message(self.conversation_id,'user',question)
        self.messages.append({'role':'user','content':question})
        self.render_chat()
        self.notice.setText('Analysing evidence in small batches. Deep research may take several minutes…')
        history=[{'role':m['role'],'content':m['content']} for m in self.messages[:-1]]
        selected=self.scope.currentData()
        model=self.model.currentText()
        def answer():return RAGEngine(self.get_store()).ask(question,document_ids=[selected] if selected else None,history=history,model=model)
        def done(result):
            self.chats.add_message(self.conversation_id,'assistant',result['answer'],result['sources'])
            self.messages.append({'role':'assistant','content':result['answer'],'sources':result['sources']})
            if len(self.messages)==2:self.chats.rename_conversation(self.conversation_id,question[:60])
            self.render_chat()
            self.refresh_history()
            self.notice.setText('Answer ready. Review the source passages beneath it.')
        self.run_job(answer,done)

    def open_source(self,url):
        if url.scheme()!='source':return
        source=self.source_links[int(url.path())]
        path=config.DOCUMENTS_DIR/Path(source['source_filename']).name
        dialog=QDialog(self); dialog.setWindowTitle(path.name); dialog.resize(850,700)
        layout=QVBoxLayout(dialog); excerpt=QLabel(source['chunk_text']); excerpt.setWordWrap(True); layout.addWidget(excerpt)
        if path.exists() and path.suffix.lower()=='.pdf' and source.get('page_number',-1)>0:
            import fitz
            with fitz.open(path) as pdf:
                page=pdf[source['page_number']-1]; pix=page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)); image=QPixmap(); image.loadFromData(pix.tobytes('png'))
            label=QLabel(); label.setPixmap(image); scroll=QScrollArea(); scroll.setWidget(label); layout.addWidget(scroll,1)
        dialog.exec()

    def visualize(self,kind):
        from modules.visuals import render_diagram,render_data
        path,_=QFileDialog.getSaveFileName(self,'Save visual',str(Path.home()/'DocMind-visual.png'),'PNG (*.png);;SVG (*.svg);;PDF (*.pdf)')
        if not path:return
        try:
            if kind=='chart':
                raw,ok=QInputDialog.getMultiLineText(self,'Chart data','Enter verified label,value pairs, one per line:')
                if not ok:return
                pairs=[line.rsplit(',',1) for line in raw.splitlines() if line.strip()]
                render_data([p[0] for p in pairs],[float(p[1]) for p in pairs],path)
            else:
                answer=next((m['content'] for m in reversed(self.messages) if m['role']=='assistant'),'')
                render_diagram(answer,path,kind)
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as exc: QMessageBox.warning(self,'Visual not created',str(exc))

    def export_chat(self):
        if not self.messages:return
        path,_=QFileDialog.getSaveFileName(self,'Export report',str(Path.home()/'DocMind-report.docx'),'Word (*.docx);;PDF (*.pdf);;Text (*.txt)')
        if not path:return
        from modules.reports import save_report
        try: save_report(path,self.messages)
        except Exception as exc: QMessageBox.warning(self,'Export failed',str(exc))

    def closeEvent(self,event):
        if self.operation_busy:
            QMessageBox.information(self,"Please wait","Finish the current task before closing."); event.ignore()
        else: event.accept()

    def clear_data(self):
        if QMessageBox.warning(self,'Delete all DocMind data','This permanently deletes your locally stored documents, search index, and chat history. Continue?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        if self.operation_busy:
            QMessageBox.information(self,'Please wait','Finish the current operation before deleting data.')
            return
        self.store=None
        self.chats=None
        import gc
        gc.collect()
        for directory in (config.DOCUMENTS_DIR,config.DATABASE_DIR,config.EXPORTS_DIR):
            if directory.exists():
                shutil.rmtree(directory,ignore_errors=False)
            directory.mkdir(parents=True,exist_ok=True)
        self.chats=ChatManager()
        self.new_chat()
        self.refresh_documents()
        self.notice.setText('Local DocMind data deleted. Files outside DocMind were not changed.')


def main():
    app=QApplication(sys.argv)
    app.setApplicationName('DocMind')
    app.setStyle("Fusion")
    window=MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__=='__main__':
    main()
