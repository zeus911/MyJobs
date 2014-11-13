===========
Job Posting
===========

Overview
========
The new job posting feature allows purchased microsite owners to create and sell
products individually or in groups. Any My.jobs user, then has the ability to
purchase these products to post job listings, subject to a moderator's
approval. The only prerequisite to using the job posting feature is the
existence of a site-package, which may be created by a DirectEmployers staff
member.

Product Life Cycle
==================
A product transitions between different states throughout its life time, and
depending on that state may be interacted with in a few different ways,
depending on the user's role. What follows is a complete description of that
life cycle broken down by a user's role.

Purchased Microsite Owner
-------------------------
A purchased microsite owner can create and sell products as well as moderate
the use of those products. Before doing so, they must first have a site-package
to add that product to. Currently, requests for site-packages are fielded by
DirectEmployers staff. After fulfilling the site-package requirement, the
process of selling and managing products is pretty straight forward.

Create a product
~~~~~~~~~~~~~~~~
.. note:: Pricing a product requires that a purchased microsite owner have an
          Authorize.net account.

Creating a product is simply a matter of deciding which site-package it is
a part of, determining which company it belongs to, the price of the
product, and various details about the types of jobs that can be created
with the product.  If a purchased microsite owner wants finer grained
control over which jobs may be posted, they should ensure that the product
requires approval. 

Create a product grouping [#]_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order for products to be viewable by a user, they must first be a part of a
product grouping. In the simplest case, a product grouping will consist of a
single product, but they may be leveraged to prioritize and organize products.
For intance, it is entirely reasonable to create a "Featured Products" product
grouping.

Create an offline purchase
~~~~~~~~~~~~~~~~~~~~~~~~~~
An offline purchase represents an order that may or may not have been
fulfilled. If a purchasing company is specified, then the selected products
will appear in that company's purchased products list. If a purchasing company
is not specified, the offline purchase's redemption code may be used later to
claim the purchase.

Moderate products
~~~~~~~~~~~~~~~~~
By this point, a user now has the ability to post jobs using their purchased
products. Each job posting that is moderated may be accepted, rejected, or in
cases where it is deemed necessary, the company can be blocked from creating
future postings. If a moderated job is later edited, it will be sent for review
again before being published. 

.. [#] Future versions of this feature will deprecate the use of product
       groupings, which should streamline the entire process.
