# README Generator

This script automates the generation and publication of `README.md` files for Python projects on GitHub. It leverages Autogen's language model capabilities to create concise and professional documentation and uses Playwright to automate the GitHub publishing process.

## Key Features

- **Automated README Generation:**  Uses a large language model to generate a `README.md` file based on the provided Python script.
- - **GitHub Publishing:** Automates the process of creating or updating a `README.md` file within a specified GitHub repository.
  - - **Customizable:**  Requires user input for the folder path and Python file name.  Utilizes environment variables for sensitive information.
   
    - ## How to Use
   
    - 1.  **Prerequisites:**
      2.      *   Install the required Python packages: `pip install autogen-core playwright python-dotenv`
      3.      *   Install Playwright browsers: `playwright install`
      4.      *   Set the following environment variables in a `.env` file:
      5.          *   `GITHUB_EMAIL`: Your GitHub email address.
      6.              *   `GITHUB_PASSWORD`: Your GitHub password.
      7.                  *   `GITHUB_REPO_URL`: The URL of the GitHub repository (e.g., `https://github.com/your-username/your-repo`).
      8.              	    *	`GITHUB_REPO_FOLDER`: Folder to upload README to (e.g. autogen/post)
      9.              	        *   `GEMINI_API_KEY`: Your Gemini API key.
      10.              	    2.  **Run the script:**
      11.              	    ```bash
      12.              	    python your_script_name.py
      13.              	    ```
      14.              	3.  **Provide Input:**
      15.               *   The script will prompt you to enter the folder path containing your Python script and the name of the Python file.
      16.               *   Manually complete 2FA verification in the browser.
      17.           4.  **Review:** The script will generate a README.md file, upload it to the specified GitHub repository, and notify you when completed.
      18.       
