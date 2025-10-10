import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt
from ui.splash import SplashScreen
from ui.login import LoginPage
from ui.dashboard import DashboardPage
from ui.simulator import SimulatorPage
from ui.settings import SettingsPage
from ui.about import AboutPage

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.splash = SplashScreen(self.show_login)
        self.splash = SplashScreen(self.show_login)
        self.login = LoginPage(self.show_dashboard)
        self.dashboard = DashboardPage(self.show_simulator, self.show_settings, self.show_about)
        self.simulator = SimulatorPage()
        self.settings = SettingsPage()
        self.about = AboutPage()

        for page in [self.splash, self.login, self.dashboard, self.simulator, self.settings, self.about]:
            self.addWidget(page)

        self.setCurrentWidget(self.splash)
        # self.setFixedSize(1620, 880)
        # self.showFullScreen()
        self.setWindowTitle("CCTS Desktop Application")

    def show_login(self):
        self.setCurrentWidget(self.login)
    def close_application(self):
        self.close()
        self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint)
        self.show()



    def show_dashboard(self):
        self.setCurrentWidget(self.dashboard)

    def show_simulator(self):
        self.setCurrentWidget(self.simulator)

    def show_settings(self):
        self.setCurrentWidget(self.settings)

    def show_about(self):
        self.setCurrentWidget(self.about)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
