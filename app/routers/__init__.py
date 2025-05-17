from .health import ping
import app.routers.user as user
import app.routers.account as account
import app.routers.history as history
import app.routers.prediction as prediction
import app.routers.report as report

def add_route(route, routers, tags):
    prefix = '/api'
    routers.append({
        'router': route,
        'tags': tags,
        'prefix': prefix
    })

routers = []

routers.append({
    'router': ping.router
})
add_route(user.router, routers, user.router.tags)
add_route(account.router, routers, account.router.tags)
add_route(history.router, routers, history.router.tags)
add_route(prediction.router, routers, prediction.router.tags)
add_route(report.router, routers, report.router.tags)