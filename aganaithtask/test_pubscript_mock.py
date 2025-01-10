
import pytest
import requests
from unittest.mock import patch, MagicMock
import os
import xml.etree.ElementTree as ET

# Function to simulate API responses
def mock_requests_get(url, *args, **kwargs):
    if "esearch.fcgi" in url:
        # Mock response for esearch API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <eSearchResult>
            <Count>1</Count>
            <IdList>
                <Id>12345678</Id>
            </IdList>
        </eSearchResult>
        """
        return mock_response
    elif "esummary.fcgi" in url:
        # Mock response for esummary API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <eSummaryResult>
            <DocSum>
                <Item Name="Title">Sample Article Title</Item>
                <Item Name="PubDate">2025</Item>
                <Item Name="Author">Author One</Item>
                <Item Name="Author">Author Two</Item>
                <Item Name="Affil">Sample Institution</Item>
                <Item Name="Email">author@example.com</Item>
            </DocSum>
        </eSummaryResult>
        """
        return mock_response
    else:
        # Default mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        return mock_response


# Test cases
@patch('requests.get', side_effect=mock_requests_get)
def test_valid_query_with_filename(mock_get):
    # Simulate user inputs
    query = "COVID-19"
    option = "-f"
    filename = "testfile.csv"

    # Run the script logic
    from pubmed_script import main
    main(query, option, filename)

    # Check if the file was created
    assert os.path.exists(filename)
    
    # Verify file content
    with open(filename, 'r') as f:
        content = f.read()
    assert "Sample Article Title" in content
    assert "2025" in content
    assert "Author One, Author Two" in content
    assert "Sample Institution" in content
    assert "author@example.com" in content

    # Clean up
    os.remove(filename)


@patch('requests.get', side_effect=mock_requests_get)
def test_valid_query_without_filename(mock_get):
    # Simulate user inputs
    query = "Cancer"
    option = ""
    filename = None

    # Run the script logic
    from pubmed_script import main
    main(query, option, filename)

    # Check if the timestamped file was created
    files = [f for f in os.listdir('.') if f.startswith('fetched') and f.endswith('.csv')]
    assert len(files) == 1
    filepath = files[0]

    # Verify file content
    with open(filepath, 'r') as f:
        content = f.read()
    assert "Sample Article Title" in content
    assert "2025" in content
    assert "Author One, Author Two" in content
    assert "Sample Institution" in content
    assert "author@example.com" in content

    # Clean up
    os.remove(filepath)


@patch('requests.get', side_effect=mock_requests_get)
def test_no_results_found(mock_get):
    # Modify mock response for no results
    def no_results_mock(url, *args, **kwargs):
        if "esearch.fcgi" in url:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<eSearchResult><Count>0</Count><IdList></IdList></eSearchResult>"
            return mock_response
        return mock_requests_get(url, *args, **kwargs)

    mock_get.side_effect = no_results_mock

    # Simulate user inputs
    query = "NonexistentQuery12345"
    option = ""

    # Run the script logic
    from pubmed_script import main
    main(query, option)

    # Verify console output (use capsys fixture in pytest for console output verification)
    captured = capsys.readouterr()
    assert "No PubMed IDs found." in captured.out


@patch('requests.get', side_effect=mock_requests_get)
def test_help_option(mock_get, capsys):
    # Simulate user input for help
    query = ""
    option = "-h"

    # Run the script logic
    from pubmed_script import main
    main(query, option)

    # Verify console output
    captured = capsys.readouterr()
    assert "Enter the Book name for book metadata" in captured.out
    assert "Default metadata is generated" in captured.out
