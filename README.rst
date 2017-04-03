=======================================
Network Equipment Configuration Toolkit
=======================================

What is "NECT"?
---------------

NECT is an earnest attempt at a network equipment configuration parser that
enables the user to change the model and/or vendor of their new equipment
without the need to know all of the required CLI commands. Inspired by the
*fantastic*
`CiscoConfParse library
<http://www.pennington.net/py/ciscoconfparse/intro.html>`_,
NECT takes it one step further to help network engineers and sysadmins make the
transition to a new vendor much, much easier.

What can/will it do?
--------------------

Read in a configuration file from your equipment and convert it to a
vendor-free format. It can be a complete configuration or just sections you've
cut out. Interface names, VLAN tagging, stacking, compatible commands, etc. are
all handled for you where possible.

You can:

* Change VLAN names
* Add AAA parameters
* Modify interface configuration
* Add memembers to a stack
* Change the target model

When you're done, spit it back out to a target model configuration. Section
ordering and syntax are all done for you; you can save it as the startup-config
or copy-paste into the configuration terminal.

What can't it do?
-----------------

Sadly, not every configuration line can be converted. For example, alias
commands are vendor-specific and targeted for a very narrow purpose. It's
impossible to read something like that and just know what exactly you want done
with it. You also have password hashes (ex. Cisco type 4 and Aruba SHA256) that
you won't be able to read in and convert on-the-fly. While we will try to
accommodate for this, there will never be 100% coverage and compatibility.

But that's ok; this is here to *help* you, not replace you.

----

Why bother?
^^^^^^^^^^^

I've had several engineers criticize my attempt to create a project such as
this. See my response in the documentation.
