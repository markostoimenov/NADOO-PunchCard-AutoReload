"""
the best app in the world of all times quack
"""

import os
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import sqlite3
from datetime import datetime
import csv


class PunchClock(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        self.conn = sqlite3.connect('punch_clock.db')
        self.create_table()
        self.clear_log()

        self.check_in_button = toga.Button(
            'Check In',
            on_press=self.check_in,
            style=Pack(padding=5)
        )
        self.check_out_button = toga.Button(
            'Check Out',
            on_press=self.check_out,
            style=Pack(padding=15)
        )
        self.log_label = toga.Label(
            'Punch Log:',
            style=Pack(padding=(10, 0))
        )
        self.log_box = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))

        self.refresh_log()

        self.generate_report_button = toga.Button(
            'Generate Report',
            on_press=self.generate_report,
            style=Pack(padding=5)
        )

        if os.getenv('ENV') == 'DEV':
            self.reload_button = toga.Button(
                'Reload',
                on_press=self.reload_app,
                style=Pack(padding=5)
            )


        main_box.add(self.check_in_button)
        main_box.add(self.check_out_button)
        main_box.add(self.log_label)
        main_box.add(self.log_box)
        main_box.add(self.generate_report_button)

        if os.getenv('ENV') == 'DEV':
            main_box.add(self.reload_button)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def create_table(self):
        """Create a table if it doesn't exist to store punch times."""
        try:
            with self.conn:
                self.conn.execute('''CREATE TABLE IF NOT EXISTS punch_log (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            action TEXT,
                                            timestamp TEXT
                                    )''')
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")

    def clear_log(self):
        """Clear the punch log on startup."""
        with self.conn:
            self.conn.execute('DELETE FROM punch_log')        

    def refresh_log(self):
        """Refresh the log display with current punch data."""
        self.log_box.value = ""
        cursor = self.conn.execute("SELECT action, timestamp FROM punch_log ORDER BY id DESC")
        for row in cursor:
            self.log_box.value += f"{row[1]}: {row[0]}\n"

    def check_in(self, widget):
        """Record the check-in time."""
        self.record_punch('Check In')

    def check_out(self, widget):
        """Record the check-out time."""
        self.record_punch('Check Out')

    def record_punch(self, action):
        """Record the punch action and time."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.conn:
            self.conn.execute("INSERT INTO punch_log (action, timestamp) VALUES (?, ?)", (action, timestamp))
        self.refresh_log()

    def generate_report(self, widget):
        """Generate a CSV report of all punch times."""
        try:
            # Provide an absolute path to the project directory
            project_dir = '/home/dci-students/CODE/PunchClock/punch_clock/src/punch_clock'
            report_path = os.path.join(project_dir, 'punch_log_report.csv')
            print(f"Generating report at: {report_path}")

            with open(report_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['ID', 'Action', 'Timestamp'])  # Write CSV headers
                cursor = self.conn.execute("SELECT id, action, timestamp FROM punch_log")
                for row in cursor:
                    csvwriter.writerow(row)  # Write rows from the punch_log table
            print(f"Report written successfully to {report_path}")
        except Exception as e:
            print(f"An error occurred while generating the report: {e}")

    def reload_app(self, widget):
        """Reload the application interface."""
        # Remove current content
        self.main_window.content = None
        # Re-run startup to rebuild the interface
        self.startup()        

    def exit(self):
        """Clean up when the app is closed."""
        self.conn.close()
        return super().exit()
        
def main():
    return PunchClock()

if __name__ == '__main__':
    main().main_loop()
