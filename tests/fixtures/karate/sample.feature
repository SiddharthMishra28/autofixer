Feature: Login API validations

@login @regression
Scenario: SCN-101 successful login
  Given path '/login'
  When method post
  Then status 200
  And match response.user.id == '#number'
  And match response.user.role == 'admin'

Scenario: fallback check
  * def expected = 'ok'
  * match response.meta.status == expected
