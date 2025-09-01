import pytest
import sys
from unittest import mock
import main

# Test case 1:
@mock.patch('argparse.ArgumentParser.parse_args')
def test_main_valid_url(mock_args):
    """
    Checks that main() returns 0 for a valid URL and runs the crawler.
    """
    # Mock valid args and run main
    mock_args.return_value = mock.Mock(base_url='example.com')
    with mock.patch('crawler.crawler.Crawler') as MockCrawler:
        instance = MockCrawler.return_value
        instance.base_url = 'https://example.com'
        instance.start = mock.AsyncMock()
        with mock.patch('asyncio.run') as mock_run:
            mock_run.return_value = None
            assert main.main() == 0
            mock_run.assert_called_once()

# Test case 2:
@mock.patch('argparse.ArgumentParser.parse_args')
def test_main_invalid_url(mock_args):
    """
    Checks that main() returns 1 and prints error for invalid URL.
    """
    # Mock invalid args and run main
    mock_args.return_value = mock.Mock(base_url='not a url')
    with mock.patch('crawler.crawler.Crawler', side_effect=ValueError("Invalid base URL 'not a url': Invalid domain format: not a url")):
        with mock.patch('builtins.print') as mock_print:
            assert main.main() == 1
            mock_print.assert_any_call("Error: Invalid base URL 'not a url': Invalid domain format: not a url")

# Test case 3:
@mock.patch('argparse.ArgumentParser.parse_args')
def test_main_unexpected_error(mock_args):
    """
    Checks that main() returns 1 and prints error for unexpected exception.
    """
    # Mock unexpected error and run main
    mock_args.return_value = mock.Mock(base_url='example.com')
    with mock.patch('crawler.crawler.Crawler') as MockCrawler:
        instance = MockCrawler.return_value
        instance.base_url = 'https://example.com'
        instance.start = mock.Mock()
        with mock.patch('asyncio.run', side_effect=Exception('Unexpected')):
            with mock.patch('builtins.print') as mock_print:
                assert main.main() == 1
                mock_print.assert_any_call('Unexpected error: Unexpected')
