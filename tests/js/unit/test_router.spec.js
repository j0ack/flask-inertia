
const resolver = require('resolver.js')

describe('flask-inertia router test', () => {

  it('check routes', () => {
    expect(Object.keys(window.routes)).toContain('route_without_arg')
    expect(Object.keys(window.routes)).toContain('route_with_arg')
    expect(Object.keys(window.routes)).toContain('route_with_typed_arg')
    expect(Object.keys(window.routes)).toContain('route_with_multiple_args')
  })

  it('check invalid url', () => {
    expect(
      () => window.reverseUrl('inactive')
    ).toThrow()
  })

  it('check resolver without arg', () => {
    const route = window.reverseUrl('route_without_arg')
    expect(route).toBe('/')
  })

  it('check expect no argument', () => {
    expect(
      () => window.reverseUrl('route_without_arg', 'test')
    ).toThrow()
  })

  it('check resolver with arg', () => {
    let route = window.reverseUrl('route_with_arg', 7357)
    expect(route).toBe('/7357/')

    // check named argument
    route = window.reverseUrl('route_with_arg', {user_id: 7357})
    expect(route).toBe('/7357/')

    // check list of arguments
    route = window.reverseUrl('route_with_arg', [7357])
    expect(route).toBe('/7357/')
  })

  it('check typed argument', () => {
    let route = window.reverseUrl('route_with_typed_arg', 7357)
    expect(route).toBe('/7357/')

    // check named argument
    route = window.reverseUrl('route_with_typed_arg', {user_id: 7357})
    expect(route).toBe('/7357/')

    // check list of arguments
    route = window.reverseUrl('route_with_arg', [7357])
    expect(route).toBe('/7357/')
  })

  it('check resolver wrong named arg', () => {
    expect(
      () => window.reverseUrl('route_with_arg', {another_id: 7357})
    ).toThrow()
    expect(
      () => window.reverseUrl('route_with_typed_arg', {another_id: 7357})
    ).toThrow()
  })

  it('check multiple args', () => {
    let route = window.reverseUrl('route_with_multiple_args', 7357, 'test')
    expect(route).toBe('/7357/test/')

    // check named args
    route = window.reverseUrl('route_with_multiple_args', {
      account_id: 7357,
      user_id: 'test'
    })
    expect(route).toBe('/7357/test/')

    // check list of arg
    route = window.reverseUrl('route_with_multiple_args', [7357, 'test'])
    expect(route).toBe('/7357/test/')
  })

  it('wrong number of args', () => {
    expect(
      () => window.reverseUrl('route_with_multiple_args', [7357, 'test', 3])
    ).toThrow()
  })
})
