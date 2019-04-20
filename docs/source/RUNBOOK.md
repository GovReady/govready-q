# Runbook

## Intentions:

This document assesses what's needed to operationalize Q, and other GovReady apps, in a manner that supports the following in a cloud provider:
- [Releases](#releases): frequent, automated releases of small batches (push-button or scripts)
- [Availablity](#availability): general availability of (app).govready.com and (app).dev.govready.com
  - in most cases we'll run apps on single instances (with autorestart/scaling to make sure that instance is always up), and allow releases to impose downtime
  - users of apps will tolerate scheduled downtime provided it happens humanely and non-destructively.
- [Persistence](#persistence): data persistence
- [Pricing](#pricing): predictable OpEx pricing
- [Performance](#performance): satisfactory performance
- [Backups](#backups) strategies for backup, recovery, business continuity and platform migration (minimal vendor lock-in)
- [CI](#ci): CI pipelines and the practice of continuous delivery
  - apps should always be 'releasable' and releases happen whenever they're in the interest of the business.
- [Logging/Monitoring/Metrics](#logging):
  - log aggregation and searching
  - monitoring and alerting
  - metrics (lower priority)
- [DNS](#dns): Automated DNS provisioning
- [Certs](#certs): Management of HTTPS/TLS certificates
- [RBAC](#rbac): Role-based authentication -- GovReady team members should each have their own credentials, preferably with a single provider, to access all operational entities.



As such, it's not yet a formal runbook, but can be the basis for one as the missing pieces are fleshed out.

Further, this guide (or future iterations) should consider on-premise releases of GovReady applications. Esp.
distribution of apps for release as standalone installs in other environments that are not publicly available
and possibly don't have access to Internet resources.

### Hosting strategies:

As of this writing, we are looking at two main paths for running Q in a Cloud Service Provider:

**Pivotal Web Services (PWS)***

Pivotal's implementation of Cloud Foundry as a service is PWS: Pivotal Web Services.  In this doc PWS refers to this platform, and CF or Foundry refers to any implementation of Cloud Foundry.

This doc, as of July 2016, is focused on operationalizing Q for PWS.

**AWS**

Alternatively, most apps should be releasable to AWS, so potential consumers of our apps can model the release not only into AWS, but with adaptation, into other API-driven IaaS platforms such as Azure, Google Compute or Digital Ocean.

Writing an AWS runbook is a secondary goal to having a solid platform in PWS

## <a name="releases"></a>Releases

Cloud Foundry is designed for frequent release with the `cf push` API command. The `Makefile` with this app demonstrates how to stage prerequisite resources and push those to the new instances running the applications.

**ToDo**:

- [ ] Harden scripted release process for repeatability
- [ ] Acceptance and Production releases should only occur from a centralized location (see CI/CD below)
- [ ] Acceptance and Production releases should be logged/published/displayed

## <a name="availability"></a>Availability

PWS runs atop AWS, so it's availability probably cannot be higher than the underlying platform. I cannot find any PWS SLA guarantees. The underlying AWS EC2 SLA is 10% credit for availability between 99.95% and 99.0%, 30% credit for availability less than 99.0%.  99.95% availability is yearly downtime of [4h22m](http://uptime.is/99.95).

For apps that are still in heavy development with a userbase still being established, I think a 99.5% availability ([50m weekly downtime](http://uptime.is/99.5)), including release downtime, is acceptable.

I recommend that we not code Q for live migrations, and that the release strategy is: Green-Maintenance-Green, or:
* app runs in the Green environment
* for releases,
  * route traffic to a "Maintenance underway" page (with a countdown clock)
  * in Green, stop app, release code, do migration, start app
  * route traffic back to Green environment

Q should run with a single instance, and PWS set to auto-scale a new instance if the current instance unexpected dies.  Read also releasing by [Blue-Green Deployments](http://docs.run.pivotal.io/devguide/deploy-apps/blue-green.html).



**ToDo**

- [ ] Determine Q if can support live migrations; if so then perhaps a faster Blue/maintenance/Green release can happen, or even just Blue/Green zerodowntime.
- [ ] Test PWS autoscale/autorestart
- [ ] Write the above-described release process.


## <a name="persistence"></a>Persistence

PWS offloads data persistence to 3rd-party partners in the _Marketplace_. The MySQL service is from ClearDB, the highest tier is $100/month per DB, daily backups, and 40 connections.

**ToDo**

- [ ] Test restore from backups
- [ ] Document migration off PWS

## <a name="pricing"></a>Pricing

PWS itself is priced simply by Gb of memory. Nothing else.  If Q has 3 versions running (dev, acceptance, prod) each with 512MB, then it'll cost: $32.40

**ToDo**

- [ ] Determine acceptance memory size for Q (512MB? 128?....)

## <a name="performance"></a>Performance

PWS seems to offer no tunables in terms of network, i/o or CPU. They do have integrated dashboards, so we should be able to watch for bottlenecks and consider addressing them. See the vertical scaling section of [this document](http://docs.pivotal.io/pivotalcf/1-7/devguide/deploy-apps/cf-scale.html)

**ToDo**

- [ ] Ask Pivotal Support for more information on performance tuning

## <a name="backups"></a>backups

Restores from backup needs to be addressed per [persistence section above](#persistence).  The DB is the only persistent aspect to the application itself.

However, in the event of a complete loss of PWS, we would also want:
* all application logs
* dump of recent metrics data
* dump of roles and access controls

There's no immediately available resource on dumping logs. The log docs only discuss the `--recent` flag. Third-party logging is [discussed here](https://docs.run.pivotal.io/devguide/services/log-management.html)

**ToDo**

- [ ] Investigate dumping all of the above periodically. Open support ticket.

## <a name="ci"></a>CI

This project needs

- continuous integration (tests run on every PR to GitHub)
- continuous delivery (app can be released by repeatable process)

Options via PWS Marketplace:
- (none)

Options from by dint of Pivotal sponsorship:
- Concourse.ci

Options via PWS Technology partners:
- CloudBees (hosted Jenkins)

Options via GitHub integrations:
- Travis
- CodeShip
- CircleCI
- Shippable
- BuildKite
- Semaphore
- SnapCI

**ToDo**

- [ ] Evaluate pipeline with Concourse via [blog/tutorial](https://blog.pivotal.io/pivotal-cloud-foundry/products/continuous-deployment-from-github-to-pws-via-concourse)
- [ ] Write a test harness

## <a name="logging"></a> Logging/Monitoring/Metrics

PWS has some primitives to help.

For logging, Loggregator stores limited amt on disk, so we'd need a third party 'drain' (DataDog? Sumologic?)

For metrics, PWS has a built-in metrics dashboard. Also has off-the-shelf NewRelic integration. Recommend using build-in metrics until its shown to be inadequate.

For monitoring, we should use synthetic monitors to test site availability and functionality. We should get _notifications_ when a service is restarting, or has been briefly unavailable, or has not met our metrics (e.g. response time). **If we have uptime expectations**, we should have _alarms_ that are routed to on-call via one of OpsGenie, PagerDuty or VictorOps.

**Todo**

- [ ] Q needs application level Logging -- add this
- [ ] Logging: Use Loggregator until we have log retention guidelines
- [ ] Metrics: Use PWS metrics until more functionality is needed
- [ ] Monitoring: Read and digest this page: https://docs.pivotal.io/pivotalcf/1-7/opsguide/metrics.html

## <a name="dns"></a>DNS

PWS supports routing for 'private domains', e.g. routing traffic for `q.govready.com` to a mapped applications.

**ToDo**

- [x] Test routing `qq.govready.com` to the prerelease
- [x] Document the process for mapping DNS and routes to apps

### DNS implementation and testing notes:

#### govready.pburkholder.com

Create route from http://govready.pburkholder.com to app `govready-q` in space `sandbox`.

First, create a cname:
```
govready.pburkholder.com. 59	IN	CNAME	govready-q.cfapps.io.
```
Then:

```
$ cf target -s sandbox
$ cf create-domain GovReadyPDB pburkholder.com
Creating domain pburkholder.com for org GovReadyPDB as pburkholder+govready@pobox.com...
OK
$ cf map-route govready-q pburkholder.com --hostname govready
Creating route govready.pburkholder.com for org GovReadyPDB / space sandbox as pburkholder+govready@pobox.com...
OK
Adding route govready.pburkholder.com to app govready-q in org GovReadyPDB / space sandbox as pburkholder+govready@pobox.com...
OK
```

#### APP.dev.pburkholder.com

For the development branch, changed manifest.yml to have:

```
---
applications:
- name: govready-q
  services:
     - cf-govready-q-pgsql # needs provisioning between deployments
```

and created a generic route mapping from the `development` space to `dev.pburkholder.com`:

```
cf create-route development dev.pburkholder.com
```

and then launch the app with:

```
cf push -d dev.pburkholder.com
```

To test routes independent of DNS, use Curl directly against the http endpoint:

```
curl -vs http://52.72.73.102 -H "Host: govready-q.dev.pburkholder.com"
```

In DNS, I've configured the wildcard \*.dev.pburkholder.com is a CNAME to foo.cfapps.io

```
      {
            "ResourceRecords": [
                {
                    "Value": "foo.cfapps.io"
                }
            ],
            "Type": "CNAME",
            "Name": "\\052.dev.pburkholder.com.",
            "TTL": 60
        },
```


## <a name="certs"></a>Certs

PWS provides SSL for hosted domains: https://docs.run.pivotal.io/marketplace/pivotal-ssl.html

Should we desire CDN integration, see https://docs.run.pivotal.io/marketplace/integrations/cloudflare/index.html

**ToDo**:

- [ ] Enable HTTPS for https://qq.govready.com DNS test once that's complete
- [ ] Document process (or add tooling) for additional apps.

## <a name="rbac"></a>RBAC

It seems that GSA/18f has done [due diligence for the CF UAA](https://github.com/opencontrol/cf-compliance/blob/master/UAA/component.yaml) Looks good.

**ToDo**:
- [ ] Set up root account and share with Greg
- [ ] Add Josh and Peter and Greg as users
- [ ] Document user deactivation
