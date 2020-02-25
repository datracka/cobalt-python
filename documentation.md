# Documentation

## Api Endopoints

### `/api/login` [GET]

third party login using Github outputs access token

(internally server redirects to authentication server to proceed to authorization, who redirects to `/api/callback` later on)

### `/api/get_repositories_job` [GET]

Run Job for retrieving repositories given a search

#### params

- access_token
- query_search: A search string following `https://developer.github.com/v3/search/`

Example: `"api/get_repositories?access_token=123123123123123&query_search=XXXX"`

#### returns 200 if worked out, 400 if something went wrong

### `/api/start_users_job` [GET]

Run job for retrieving users for a given search

- access_token
- query_search A search string following `https://developer.github.com/v3/search/`

Exampple: `"https://api.github.com/search/users?q=location:malaga&per_page=100"`

#### returns 200 if worked out, 400 if something went wrong

## Engine

Currently search is done solely against github.

#### Github Limitations 

Only 30 requests per minute can be done. [rate limit documentation](https://developer.github.com/v3/search/#rate-limit) For each request we do we should be sure we are not getting same results but different one.

The way we found for "paginating" through different requests was to set a time range for each request. In this way each request ask for a given range of created repo.

Note that each request itself can be composed of N request to get all paginated results (max results by request are 100 )  
[pagination] (https://developer.github.com/v3/guides/traversing-with-pagination/)

Test search query: 

- q=php+laravel+in:readme+language:php+topic:laravel
