const $ = (id) => document.getElementById(id);
const fmt = new Intl.NumberFormat('en-US');
const number = (value) => fmt.format(value);
const money = (value) => value >= 1000000 ? `$${(value / 1000000).toFixed(1)}M` : `$${Math.round(value / 1000)}K`;
const metric = (value, label) => `<div class="metric"><strong>${value}</strong><span>${label}</span></div>`;
const bar = (label, value, max, tone = '') => `<div class="bar ${tone}"><div class="bar-meta"><span>${label}</span><span>${number(value)}</span></div><div class="bar-track"><div class="bar-fill" style="width:${Math.max(4, value / max * 100)}%"></div></div></div>`;

async function loadReport() {
  const response = await fetch('/api/report');
  if (!response.ok) throw new Error('Report data unavailable');
  return response.json();
}

function render(data) {
  const { reach, geography: geo, foundersAndBusiness: people, economicImpact: econ, virtualPerformance: virtual, equityAndInclusion: equity } = data;
  const actual = econ.scenarios.find((item) => item.scenario_key === 'actual_badged');
  const registered = econ.scenarios.find((item) => item.scenario_key === 'registered_offline');
  const inPerson = reach.btwActualInPersonBadgePrinted + reach.communityPartnerEventAttendees + reach.meetupActualAttended;

  $('footprint').textContent = number(reach.estimatedGrossFootprint);
  $('heroStates').textContent = number(geo.statesRepresented);
  $('heroOrgs').textContent = number(people.uniqueOrganizations);
  $('heroImpact').textContent = money(actual.total_impact);
  $('reachMetrics').innerHTML = [
    metric(number(inPerson), 'in-person attendees'),
    metric(number(reach.youtubeUniqueViewers), 'unique digital viewers'),
    metric(number(reach.btwActiveRegistrations), 'active registrations'),
    metric(number(reach.meetupLocations), 'meetup locations'),
  ].join('');

  $('localVisitors').textContent = number(geo.localVisitors);
  const geoItems = [
    ['Local / Cincinnati', geo.localVisitors],
    ['Regional drive-in', geo.regionalVisitors],
    ['Overnight visitors', geo.overnightVisitors],
    ['Out-of-state', geo.outOfStateVisitors],
  ];
  $('geoBars').innerHTML = geoItems.map(([label, value], index) => bar(label, value, geo.localVisitors, index > 1 ? 'secondary' : '')).join('');

  $('founders').textContent = number(people.founders);
  $('peopleMetrics').innerHTML = [
    metric(number(people.executives), 'executives'),
    metric(number(people.uniqueOrganizations), 'organizations'),
    metric(number(people.sessionScans), 'session scans'),
    metric('21', 'speaker sessions'),
  ].join('');
  $('markets').innerHTML = geo.topMarkets.slice(0, 6).map((item) => `<div class="market"><strong>${number(item.attendees)}</strong><span>${item.label}</span></div>`).join('');

  $('impactMetrics').innerHTML = [
    `<div class="impact-card"><strong>${money(actual.total_impact)}</strong><span>modeled actual-attendee impact</span><p>Visitor spending, local organizer activity, and induced impact in one regional story.</p></div>`,
    `<div class="impact-card"><strong>${money(registered.total_impact)}</strong><span>modeled registered-onsite scenario</span><p>A scenario-based view of the opportunity created by the full registered audience.</p></div>`,
    `<div class="impact-card"><strong>${money(actual.visitor_spending)}</strong><span>visitor spending</span><p>Travel, food, nightlife, retail, and hospitality activity connected to the event.</p></div>`,
    `<div class="impact-card"><strong>${number(Math.round(actual.room_nights))}</strong><span>modeled room nights</span><p>Overnight stays that translate event participation into local economic activity.</p></div>`,
  ].join('');

  $('virtualMetrics').innerHTML = [
    metric(number(virtual.totals.views), 'views'),
    metric(number(virtual.totals.uniqueViewers), 'unique viewers'),
    metric(number(virtual.totals.watchHours.toFixed(1)), 'watch hours'),
    metric(number(virtual.totals.subscribersGained), 'subscribers gained'),
  ].join('');
  const maxStream = Math.max(...virtual.streams.map((stream) => stream.uniqueViewers));
  $('streamBars').innerHTML = virtual.streams.map((stream) => bar(stream.title, stream.uniqueViewers, maxStream)).join('');

  $('distressed').textContent = `${equity.distressedZipcodeRegistrationsPct.toFixed(1)}%`;
  $('raceCount').textContent = number(equity.raceEthnicity.find((item) => item.label === 'Black or African American').count);
  $('genderCount').textContent = number(equity.gender.find((item) => item.label === 'Woman').count);
}

loadReport().then(render).catch((error) => {
  console.error(error);
  document.querySelector('main').innerHTML = '<div class="wrap"><p class="kicker">Report unavailable</p><h1>Unable to load aggregate report data.</h1></div>';
});

