# How to use
1. Install dependencies with `pipenv install`
2. Copy `.env.example` and create `.env` file
3. Login to the website then go to model profile that you already have a subscription
4. Use Developer Tools to monitor API call to /getPost. Note the query parameters.
5. Fill in `.env` with query parameters from step 4.
6. Run `pipenv run python main.py`
7. Files will be saved at `./output` directory