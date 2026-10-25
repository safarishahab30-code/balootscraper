import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from unittest.mock import patch
from main import run_interactive_menu

@pytest.mark.parametrize("choice, target_func", [
    ("technolife", "main.run_scraper"),
    ("custom", "main.run_custom_scrape"),
    ("url", "main.run_custom_url_scrape"),
    ("tracker", "main.run_manual_tracker"),
    ("automation", "main.run_scheduler"),
    ("files", "main.show_saved_files"),
])
def test_all_menu_actions(choice, target_func):
    """تست اجرای تک‌تک گزینه‌ها و سپس خروج موفق"""
    with patch("main.farsi_menu") as mock_menu, \
         patch(target_func) as mock_action:
        
        # ابتدا گزینه مورد نظر انتخاب می‌شود و سپس خروج
        mock_menu.side_effect = [choice, "exit"]
        
        run_interactive_menu()
        
        assert mock_action.called


def test_menu_direct_exit():
    """تست خروج مستقیم از منو"""
    with patch("main.farsi_menu") as mock_menu:
        mock_menu.return_value = "exit"
        
        run_interactive_menu()
        
        assert mock_menu.called
