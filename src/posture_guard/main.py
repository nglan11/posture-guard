"""Desktop entry point."""
def main():
    from posture_guard.ui.main_window import MainWindow
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
