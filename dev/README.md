# test-results-dashboard development

## Initialise or recreate database

```
delete_dashboard_then_create_empty.py
```

## Start development server on port 8811

```
start.py
```
http://localhost:8811/results

## Load test data

Start development server on port 8811 first
```
load_test_data.py
```

## Run a single test
```
manage.py test results.tests.AddTestResultTests.test_can_log_simple_txt_file
```

## Run all tests
```
manage.py test results
```
