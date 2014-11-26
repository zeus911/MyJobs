import datetime


two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)
one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
one_month_ago = datetime.datetime.now() - datetime.timedelta(months=1)


# One job for 2 day ago, one for 1 week ago, and one for 1 month ago.
jobs = """
<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"><channel><title>Jobs</title><link>http://rushenterprises-veterans.jobs</link><description>Jobs</description><atom:link href="http://rushenterprises-veterans.jobs/alabama/usa/jobs/feed/rss" rel="self"></atom:link><language>en-us</language><lastBuildDate>Tue, 21 Oct 2014 22:21:33 -0400</lastBuildDate><item><title>(USA-AL-Mobile) Frame Technician</title><link>http://rushenterprises-veterans.jobs/4080A6628B164B2A9C697096A9AFA54925</link><description>Requisition Number 14-2633
Post Date 10/21/2014
Title Frame Technician
Location RTC Mobile
Status Full-Time
City Mobile
State AL
Description
Frame Technician

The frame technician is responsible for repairs to damaged frame and suspension parts on heavy and medium duty trucks.

Rush Enterprises is a premier provider of quality products and services to commercial equipment users. We are customer-focused, people-oriented, and financially motivated to deliver excellent outcomes for customers, shareholders, vendors and our people.

We offer a rewarding career with a leader in the transportation industry. Grow with us as we continue to expand our network of locations and services. Rush Enterprises is always looking for good people to join our team.

Responsibilities

* Examine damaged vehicles and estimates cost of repairs. Report any hidden damage to supervisor immediately.
* Coordinate work with metal technicians.
* Accurately measure frames for mash/side sway/collapse/diamond conditions and document.
* Section frames at factory specked areas (lengthen or shorten).
* Troubleshoot and diagnose alignment problems.
* Perform front and/or rear alignments.
* Suspension work – replace components as needed.
* Repair, replace, and/or straighten frame rails.
* Straighten bent frames with pneumatic frame straightening machine to factory specifications.
* Repair or replace defective mechanical parts.
* Inspect completed repairs and drive vehicle prior to final quality check by supervisor.
Benefits

We offer exceptional compensation and benefits, 401K and stock purchase, incentives for performance, training, and opportunity for advancement - all in a culture that appreciates and rewards excellence, a positive attitude and integrity.

Requirements
Basic Qualifications

* High school diploma or general education degree (GED).
* One year experience in commercial vehicle frame repair.
Rush Enterprises (NASDAQ: RUSHA &amp; RUSHB)operates the largest network of heavy and medium- duty truck dealerships in North America. Its current truck operations include a network of locations throughout the United States. These dealerships provide an integrated, one-stop sales and service of new and used heavy- and medium-duty trucks and construction equipment, aftermarket parts, service and body shop capabilities, chrome accessories, tires and a wide array of financial services including the financing of truck and equipment sales, insurance products and leasing and rentals.

Rush Enterprises and its Affiliate Companies are Equal Opportunity Employers. All qualified applicants will receive consideration for employment without regard to race, religion, color, national origin, sex, age, status as a protected veteran, among other things, or status as a qualified individual with disability.


* All qualified applicants will receive consideration for employment without regard to race, color, religion, sex, or national origin. We are also an equal opportunity employer of individuals with disabilities and protected veterans.
* Please view Equal Employment Opportunity Posters provided by OFCCPhere.</description><pubDate>%s</pubDate><guid>http://rushenterprises-veterans.jobs/4080A6628B164B2A9C697096A9AFA54925</guid></item><item><title>(USA-AL-Mobile) Diesel Mechanic Level 5</title><link>http://rushenterprises-veterans.jobs/B4789A68107942C6914AA763FA67F85A25</link><description>Requisition Number 14-2632
Post Date 10/21/2014
Title Diesel Mechanic Level 5
Location RTC Mobile
Status Full-Time
City Mobile
State AL
Description
Diesel Mechanic V

A Diesel Mechanic is responsible for providing service to our customers while maintaining exceptional customer service. This can include: cleaning, maintenance, visual inspection, and removal of parts and attachments. Installation with the help of proper manuals, report writing, disassembly, assembly, parts reuse evaluation, and reconditioning.

Rush Truck Centers is a premier provider of quality products and services to commercial equipment users. We are customer-focused, people-oriented, and financially motivated to deliver excellent outcomes for customers, shareholders, vendors and our people.

We offer a rewarding career with a leader in the transportation industry. Grow with us as we continue to expand our network of locations and services. Rush Enterprises is always looking for good people to join our team.

Responsibilities

* Provide technical service to vehicles and equipment.
* Perform general and detailed repair of all trucks, engines and components.
* Overhaul gas or diesel engines.
* Install injectors, pistons, liners, cam shafts, cylinder heads, rod and main bearings, oil pans, clutches, fan hubs, differentials, fifth wheels, brakes, change or recharge batteries, and replace transmissions and other parts.
* Read job order, observe and listen to vehicle in operation to determine malfunction and plan work procedures.
* Examine protective guards, loose bolts, and specified safety devices on trucks, and make adjustments as needed.
* Lubricate moving parts and drive repaired vehicle to verify conformance to specifications.
* Tag all warranty parts and returns to warranty clerk.
* Attend training classes and keep abreast of factory technical bulletins.
* Develop and maintain positive relationships with customers to increase overall customer satisfaction.
Benefits

We offer exceptional compensation and benefits, 401K and stock purchase, incentives for performance, training, and opportunity for advancement - all in a culture that appreciates and rewards excellence, a positive attitude and integrity.

Requirements
Basic Qualifications

* High school diploma or general education degree (GED)
* 9 years’ experience as a Class 7 &amp; 8 technician in a dealership or related truck service facilityRush Enterprises (NASDAQ: RUSHA &amp; RUSHB)operates the largest network of heavy and medium- duty truck dealerships in North America. Its current truck operations include a network of locations throughout the United States. These dealerships provide an integrated, one-stop sales and service of new and used heavy- and medium-duty trucks and construction equipment, aftermarket parts, service and body shop capabilities, chrome accessories, tires and a wide array of financial services including the financing of truck and equipment sales, insurance products and leasing and rentals.
Rush Enterprises and its Affiliate Companies are Equal Opportunity Employers.  All qualified applicants will receive consideration for employment without regard to race, religion, color, national origin, sex, age, status as a protected veteran, among other things, or status as a qualified individual with disability.


* All qualified applicants will receive consideration for employment without regard to race, color, religion, sex, or national origin. We are also an equal opportunity employer of individuals with disabilities and protected veterans.
* Please view Equal Employment Opportunity Posters provided by OFCCPhere.</description><pubDate>%s</pubDate><guid>http://rushenterprises-veterans.jobs/B4789A68107942C6914AA763FA67F85A25</guid></item><item><title>(USA-AL-Mobile) Diesel Mechanic Level 4</title><link>http://rushenterprises-veterans.jobs/17AF1A8482F64FF78B6F75B4C302189D25</link><description>Requisition Number 14-2590
Post Date 10/20/2014
Title Diesel Mechanic Level 4
Location RTC Mobile
Status Full-Time
City Mobile
State AL
Description
Diesel Mechanic IV

A Diesel Mechanic is responsible for providing service to our customers while maintaining exceptional customer service. This can include: cleaning, maintenance, visual inspection, and removal of parts and attachments. Installation with the help of proper manuals, report writing, disassembly, assembly, parts reuse evaluation, and reconditioning.

Rush Truck Centers is a premier provider of quality products and services to commercial equipment users. We are customer-focused, people-oriented, and financially motivated to deliver excellent outcomes for customers, shareholders, vendors and our people.

We offer a rewarding career with a leader in the transportation industry. Grow with us as we continue to expand our network of locations and services. Rush Enterprises is always looking for good people to join our team.

Responsibilities

* Provide technical service to vehicles and equipment.
* Perform general and detailed repair of all trucks, engines and components.
* Overhaul gas or diesel engines.
* Install injectors, pistons, liners, cam shafts, cylinder heads, rod and main bearings, oil pans, clutches, fan hubs, differentials, fifth wheels, brakes, change or recharge batteries, and replace transmissions and other parts.
* Read job order, observe and listen to vehicle in operation to determine malfunction and plan work procedures.
* Examine protective guards, loose bolts, and specified safety devices on trucks, and make adjustments as needed.
* Lubricate moving parts and drive repaired vehicle to verify conformance to specifications.
* Tag all warranty parts and returns to warranty clerk.
* Attend training classes and keep abreast of factory technical bulletins.
* Develop and maintain positive relationships with customers to increase overall customer satisfaction.
Benefits

We offer exceptional compensation and benefits, 401K and stock purchase, incentives for performance, training, and opportunity for advancement - all in a culture that appreciates and rewards excellence, a positive attitude and integrity.

Requirements
Basic Qualifications

* High school diploma or general education degree (GED)
* 7 years’ experience as a Class 7 &amp; 8 technician in a dealership or related truck service facility.Rush Enterprises (NASDAQ: RUSHA &amp; RUSHB)operates the largest network of heavy and medium- duty truck dealerships in North America. Its current truck operations include a network of locations throughout the United States. These dealerships provide an integrated, one-stop sales and service of new and used heavy- and medium-duty trucks and construction equipment, aftermarket parts, service and body shop capabilities, chrome accessories, tires and a wide array of financial services including the financing of truck and equipment sales, insurance products and leasing and rentals.
Rush Enterprises and its Affiliate Companies are Equal Opportunity Employers.  All qualified applicants will receive consideration for employment without regard to race, religion, color, national origin, sex, age, status as a protected veteran, among other things, or status as a qualified individual with disability.


* All qualified applicants will receive consideration for employment without regard to race, color, religion, sex, or national origin. We are also an equal opportunity employer of individuals with disabilities and protected veterans.
* Please view Equal Employment Opportunity Posters provided by OFCCPhere.</description><pubDate>%s</pubDate><guid>http://rushenterprises-veterans.jobs/17AF1A8482F64FF78B6F75B4C302189D25</guid></item></channel></rss>
""" % (two_days_ago, two_days_ago, one_week_ago)


no_jobs = """
<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"><channel><title>Jobs</title><link>http://rushenterprises-veterans.jobs</link><description>Jobs</description><atom:link href="http://rushenterprises-veterans.jobs/alabama/usa/jobs/feed/rss" rel="self"></atom:link><language>en-us</language><lastBuildDate>Wed, 26 Nov 2014 09:31:18 -0000</lastBuildDate></channel></rss>
"""