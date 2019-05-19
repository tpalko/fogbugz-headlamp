import sys

sys.path.append('/media/storage/development/projects/fogbugz-headlamp')

import logging
import traceback
from datetime import datetime
from flask import g
from webapp.dao.project import ProjectDAO
from webapp.dao.milestone import MilestoneDAO
from webapp.dao.deliverable import DeliverableDAO
import re
from webapp import app
from webapp.invoicing.models import Project, Milestone, Case, CaseEvent, FogbugzUser, FogbugzUserCase, Category, Deliverable, Invoice, Company, Customer

'''
ixBug,ixBugParent,ixBugChildren,tags,fOpen,sTitle,sOriginalTitle,sLatestTextSummary,ixBugEventLatestText,ixProject,sProject,ixArea,sArea,ixGroup,ixPersonAssignedTo,sPersonAssignedTo,sEmailAssignedTo,ixPersonOpenedBy,ixPersonClosedBy,ixPersonResolvedBy,ixPersonLastEditedBy,ixStatus,sStatus,ixBugDuplicates,ixBugOriginal,ixPriority,sPriority,ixFixFor,sFixFor,dtFixFor,sVersion,sComputer,hrsOrigEst,hrsCurrEst,hrsElapsedExtra,hrsElapsed,c,sCustomerEmail,ixMailbox,ixCategory,sCategory,dtOpened,dtResolved,dtClosed,ixBugEventLatest,dtLastUpdated,fReplied,fForwarded,sTicket,ixDiscussTopic,dtDue,sReleaseNotes,ixBugEventLastView,dtLastView,ixRelatedBugs,sScoutDescription,sScoutMessage,fScoutStopReporting,dtLastOccurrence,fSubscribed,dblStoryPts,nFixForOrder,events,minievents,ixKanbanColumn2

<case ixbug="1629" operations="edit,assign,resolve,email"><ixbug>1629</ixbug><ixbugparent>0</ixbugparent><fopen>true</fopen><stitle><![CDATA[remove child gates/mounts, cabinet locks]]></stitle><soriginaltitle><![CDATA[remove child gates/mounts, cabinet locks]]></soriginaltitle><slatesttextsummary></slatesttextsummary><ixbugeventlatesttext>0</ixbugeventlatesttext><ixproject>11</ixproject><sproject><![CDATA[Property Management]]></sproject><ixarea>26</ixarea><sarea><![CDATA[124 Lincoln]]></sarea><ixpersonassignedto>2</ixpersonassignedto><spersonassignedto><![CDATA[Tim Palko]]></spersonassignedto><semailassignedto><![CDATA[tim@palkosoftware.com]]></semailassignedto><ixpersonopenedby>2</ixpersonopenedby><ixpersonclosedby>0</ixpersonclosedby><ixpersonresolvedby>0</ixpersonresolvedby><ixpersonlasteditedby>2</ixpersonlasteditedby><ixstatus>30</ixstatus><sstatus><![CDATA[Active]]></sstatus><ixpriority>3</ixpriority><spriority><![CDATA[Must Fix - Normal Priority]]></spriority><ixfixfor>178</ixfixfor><sfixfor><![CDATA[124 Lincoln 2nd Unit Rentability]]></sfixfor><dtfixfor>2018-09-30T04:00:00Z</dtfixfor><sversion></sversion><scomputer></scomputer><hrsorigest>0</hrsorigest><hrscurrest>0</hrscurrest><hrselapsedextra>0</hrselapsedextra><hrselapsed>0</hrselapsed><c>0</c><scustomeremail></scustomeremail><ixmailbox>0</ixmailbox><ixcategory>6</ixcategory><dtopened>2018-10-10T14:14:02Z</dtopened><dtresolved></dtresolved><dtclosed></dtclosed><ixbugeventlatest>10074</ixbugeventlatest><freplied>false</freplied><fforwarded>false</fforwarded><sticket><![CDATA[1629_rn95dbe8hkoui9k7]]></sticket><ixdiscusstopic>0</ixdiscusstopic><dtdue></dtdue><ixbugeventlastview>10074</ixbugeventlastview><dtlastview></dtlastview><dblstorypts>0</dblstorypts><nfixfororder>999</nfixfororder><ixkanbancolumn2>0</ixkanbancolumn2><ixbugchildren></ixbugchildren><tags></tags><ixgroup>0</ixgroup><ixbugduplicates></ixbugduplicates><ixbugoriginal>0</ixbugoriginal><scategory><![CDATA[Task]]></scategory><dtlastupdated>2018-10-10T14:14:02Z</dtlastupdated><sreleasenotes></sreleasenotes><ixrelatedbugs></ixrelatedbugs><sscoutdescription></sscoutdescription><sscoutmessage></sscoutmessage><fscoutstopreporting></fscoutstopreporting><dtlastoccurrence></dtlastoccurrence><fsubscribed>false</fsubscribed><events><event ixbugevent="10073" ixbug="1629"><ixbugevent>10073</ixbugevent><evt>1</evt><sverb><![CDATA[Opened]]></sverb><ixperson>2</ixperson><ixpersonassignedto>0</ixpersonassignedto><dt>2018-10-10T14:14:02Z</dt><s></s><femail>false</femail><fhtml>false</fhtml><fexternal>false</fexternal><schanges></schanges><sformat></sformat><rgattachments></rgattachments><evtdescription><![CDATA[Opened by Tim Palko]]></evtdescription><bemail>false</bemail><bexternal>false</bexternal><sperson><![CDATA[Tim Palko]]></sperson><shtml></shtml></event><event ixbugevent="10074" ixbug="1629"><ixbugevent>10074</ixbugevent><evt>3</evt><sverb><![CDATA[Assigned]]></sverb><ixperson>2</ixperson><ixpersonassignedto>2</ixpersonassignedto><dt>2018-10-10T14:14:02Z</dt><s></s><femail>false</femail><fhtml>false</fhtml><fexternal>false</fexternal><schanges></schanges><sformat></sformat><rgattachments></rgattachments><evtdescription><![CDATA[Assigned to Tim Palko by Tim Palko]]></evtdescription><bemail>false</bemail><bexternal>false</bexternal><sperson><![CDATA[Tim Palko]]></sperson><shtml></shtml></event></events><minievents><event ixbugevent="10073" ixbug="1629"><ixbugevent>10073</ixbugevent><evt>1</evt><sverb><![CDATA[Opened]]></sverb><ixperson>2</ixperson><ixpersonassignedto>0</ixpersonassignedto><dt>2018-10-10T14:14:02Z</dt><femail>false</femail><fhtml>false</fhtml><fexternal>false</fexternal><schanges></schanges><sformat></sformat><evtdescription><![CDATA[Opened by Tim Palko]]></evtdescription><sperson><![CDATA[Tim Palko]]></sperson></event><event ixbugevent="10074" ixbug="1629"><ixbugevent>10074</ixbugevent><evt>3</evt><sverb><![CDATA[Assigned]]></sverb><ixperson>2</ixperson><ixpersonassignedto>2</ixpersonassignedto><dt>2018-10-10T14:14:02Z</dt><femail>false</femail><fhtml>false</fhtml><fexternal>false</fexternal><schanges></schanges><sformat></sformat><evtdescription><![CDATA[Assigned to Tim Palko by Tim Palko]]></evtdescription><sperson><![CDATA[Tim Palko]]></sperson></event></minievents></case>
'''

logging.basicConfig(level=logging.DEBUG)
local_logger = logging.getLogger(__name__)
ARTIFICIAL_MILESTONE_ENDDATE = datetime.strptime("2070-01-01", "%Y-%m-%d")

# - 'names' is a comma-delimited list of user names as they appear in your Fogbugz configuration
billing_names = app.config['BILLING_NAMES'].split(',')
# - 'rates' is a comma-delimited list of hourly rates at which each user in the 'names' list bills out, respectively
billing_rates = app.config['BILLING_RATES'].split(',')

rates = dict(zip(billing_names, billing_rates))

def get_date_from_iso(iso_string):
    # -- 2013-10-03T04:00:00Z
    if iso_string:
        return datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ")
    return None

def parse_cdata(string):
    return re.sub('\[CDATA\]', '', string)

def get_flasher():
    def null(message):
        pass

    return null

def get_logger():
    return local_logger

def add_object(obj):
    try:
        g.db.add(obj)
        g.db.commit()
    except:
        logger.error("Error adding %s.." % (type(obj)))
        logger.error(str(sys.exc_info()[0]))
        logger.error(str(sys.exc_info()[1]))
        traceback.print_tb(sys.exc_info()[2])
        logger.info(str(sys.exc_info()[0]))
        logger.info(str(sys.exc_info()[1]))

def is_resolved_or_closed(status):
    return status.find("Resolved") >= 0 or status.find("Closed") >= 0

def refresh(fogbugz_client, flasher=None, logger=None):

    if not flasher:
        flasher = get_flasher()

    if not logger:
        logger = get_logger()

    now = datetime.now()

    undecided_project = ProjectDAO.get(-1)
    if not undecided_project:
        undecided_project = Project(-1, 'Undecided')
        add_object(undecided_project)

    projectlist = fogbugz_client.get_projects()

    for p in projectlist.findAll("project"):

        existing_project = ProjectDAO.get(int(p.ixProject.string))

        if existing_project:
            if existing_project.sproject != p.sProject.string:
                logger.info("Updating project name %s -> %s" %(existing_project.sproject, p.sproject.string))
                existing_project.sproject = p.sproject.string
                g.db.commit()
            else:
                pass # -- project was found, but name had not changed

        else:
            new_project = Project(int(p.ixproject.string), p.sproject.string)
            add_object(new_project)
            logger.info("Added new project %s" % new_project.sproject)

    fixforlist = fogbugz_client.get_fixfors()

    for f in fixforlist.findAll('fixfor'):

        sfixfor = parse_cdata(f.sFixFor.contents[0]) if len(f.sFixFor.contents) > 0 else "-"
        #sproject = parse_cdata(f.sproject.contents[0]) if len(f.sproject.contents) > 0 else "-"
        startdate = get_date_from_iso(f.dtStart.string)
        enddate = get_date_from_iso(f.dt.string)

        # - not in the case of the Undecided milestone
        project_id = -1
        if f.ixProject.string:
            project_id = int(f.ixProject.string)

        if not enddate and app.config['FOGBUGZ_SYNC_BILLING_ONLY']:
            logger.info("Milestone %s has no end date - skipping" %(sfixfor))
            continue

        existing_milestone = g.db.query(Milestone).filter(Milestone.ixfixfor==int(f.ixFixFor.string)).first()

        if existing_milestone:

            existing_milestone_frozen_and_invoiced = existing_milestone.bfrozen and existing_milestone.binvoiced

            # - it's frozen, so don't commit anything, but we want to know if it's been changed significantly w.r.t. billing
            if existing_milestone_frozen_and_invoiced and enddate and enddate > now:
                logger.info("Frozen milestone %s now ends in the future" % existing_milestone.sfixfor)

            if existing_milestone.sfixfor != sfixfor or (existing_milestone.dt != ARTIFICIAL_MILESTONE_ENDDATE and existing_milestone.dt != enddate) or existing_milestone.dtstart != startdate:
                logger.info("Milestone %s metadata has changed" %(existing_milestone.project.sproject))
                logger.info("Existing name: '%s' vs. New name: '%s'" % (existing_milestone.sfixfor, sfixfor))
                logger.info("Existing start date: '%s' vs. New start date: '%s'" % (existing_milestone.dtstart, startdate))
                logger.info("Existing end date: '%s' vs. New end date: '%s'" % (existing_milestone.dt, enddate))
                if not (existing_milestone_frozen_and_invoiced and app.config['FOGBUGZ_SYNC_CAREFUL']):
                    logger.info("Updating changed milestone %s" % existing_milestone.project.sproject)
                    existing_milestone.update(ixfixfor=int(f.ixfixfor.string), sfixfor=sfixfor, ixproject=project_id, dt=enddate, dtstart=startdate)
                    add_object(existing_milestone)
            else:
                logger.debug("Milestone %s - no change" %(existing_milestone.sfixfor))
        else:
            #if enddate and enddate > now and app.config['FOGBUGZ_SYNC_BILLING_ONLY']:
            #    logger.info("New Milestone %s in future - skipping" %(sfixfor))
            #    continue

            # - this can happen if we're not constrained to billing sync
            # - if we were, wouldn't have made it this far..
            if not enddate:
                enddate = ARTIFICIAL_MILESTONE_ENDDATE

            # - a milestone's project may have been deleted
            milestone_project = g.db.query(Project).filter(Project.ixproject==project_id).first()
            logger.info(milestone_project)
            if not milestone_project:
                logger.info("ixproject %s not found, writing deleted project now" % project_id)
                milestone_project = Project(project_id, 'Deleted Project %s' % project_id)
                add_object(milestone_project)

            new_milestone = Milestone(int(f.ixfixfor.string), sfixfor, project_id, enddate, startdate)
            add_object(new_milestone)
            logger.info("Added new milestone %s" % new_milestone.sfixfor)

    people = fogbugz_client.get_people()

    for person in people:
        '''
        <person><ixperson>21</ixperson><sfullname><![CDATA[Access Test]]></sfullname><semail><![CDATA[timothypalko@gmail.com]]></semail><sphone></sphone><fadministrator>false</fadministrator><fcommunity>false</fcommunity><fvirtual>false</fvirtual><fdeleted>false</fdeleted><fnotify>true</fnotify><shomepage></shomepage><slocale><![CDATA[*]]></slocale><slanguage><![CDATA[*]]></slanguage><stimezonekey><![CDATA[*]]></stimezonekey><sldapuid></sldapuid><dtlastactivity>2018-07-02T20:58:34Z</dtlastactivity><frecursebugchildren>true</frecursebugchildren><fpaletteexpanded>false</fpaletteexpanded><ixbugworkingon>0</ixbugworkingon><sfrom></sfrom></person>
        '''
        db_person = g.db.query(FogbugzUser).filter(FogbugzUser.ixperson==int(person.ixPerson.string)).first()

        if not db_person:
            db_person = FogbugzUser(ixperson=int(person.ixPerson.string), sfullname=person.sFullName.string)
            logger.info("Added new FogBugz user %s" % person.sFullName.string)
            add_object(db_person)

        # TODO: search for all cases in which this person is relevant for billing and determine if any case is in a frozen or invoiced milestone
        # TODO: the rate of a person (assigned or resolving) should apply to FogbugzUserCase records individually, not on the person globally, because their rate may change over time
        if db_person.sfullname in rates and float(db_person.frate) != float(rates[db_person.sfullname]):
            logger.info("%s's rate changed from %.2f to %.2f" %(db_person.sfullname, float(db_person.frate), float(rates[db_person.sfullname])))
            db_person.frate = float(rates[db_person.sfullname])
            add_object(resolving_fogbugz_user)

    caselist = fogbugz_client.get_cases(cols="ixBug,ixPriority,sCategory,sTicket,sTitle,ixFixFor,ixProject,sStatus,ixPersonAssignedTo,ixPersonResolvedBy,hrsElapsed,hrsElapsedExtra")
    # - ixBug,sTitle,sOriginalTitle,sLatestTextSummary,ixBugEventLatestText,ixProject,sProject,ixArea,sArea,ixGroup,ixPersonAssignedTo,sPersonAssignedTo,sEmailAssignedTo,ixPersonOpenedBy,ixPersonClosedBy,ixPersonResolvedBy,ixPersonLastEditedBy,ixStatus,sStatus,ixBugDuplicates,ixBugOriginal,ixPriority,sPriority,ixFixFor,sFixFor,dtFixFor,sVersion,sComputer,hrsOrigEst,hrsCurrEst,hrsElapsedExtra,hrsElapsed,c,sCustomerEmail,ixMailbox,ixCategory,sCategory,dtOpened,dtResolved,dtClosed,ixBugEventLatest,dtLastUpdated,fReplied,fForwarded,sTicket,ixDiscussTopic,dtDue,sReleaseNotes,ixBugEventLastView,dtLastView,ixRelatedBugs,sScoutDescription,sScoutMessage,fScoutStopReporting,dtLastOccurrence,fSubscribed,dblStoryPts,nFixForOrder,events,minievents,ixKanbanColumn2
    #caselist = fogbugz_client.search(cols="ixBug,ixPriority,sCategory,sTicket,sTitle,ixFixFor,ixProject,sStatus,ixPersonAssignedTo,ixPersonResolvedBy,hrsElapsed,hrsElapsedExtra")
    cases = []
    if caselist:
        cases = caselist.findAll('case')
    #description_tag = caselist.find("description")
    #description = parse_cdata(description_tag.string)
    for c in cases:

        logger.debug("Found case %s" % c.ixBug.string)
        fb_case = g.db.query(Case).filter(Case.ixbug==int(c.ixBug.string)).first()
        milestone = g.db.query(Milestone).filter(Milestone.ixfixfor==int(c.ixFixFor.string)).first()
        resolved_or_closed = is_resolved_or_closed(c.sStatus.string)
        milestone_frozen_and_invoiced = milestone.bfrozen and milestone.binvoiced

        '''
        Alrighty, we need to reexamine how we do all this..
        First, some terminology:
            1) "frozen" means the milestone is in a "saved" state and expected to not change w.r.t. billing. maybe this means changes are accepted but notification must occur
            2) "invoiced" means the milestone has been presented to a paying client already (billing changes will have a negative impact)
        For each case we pull, we need to break down all of changes it imposes on the data into:
            1) changes that affect billing
            2) changes that don't affect billing
        For changes that don't affect billing, we can apply them freely and without further consideration.
        Changes that don't affect billing include:
            1) updates to titles, events, or priority
            2) static-rate assignment changes
        For changes that affect billing, it depends on milestone state.
        Changes that affect billing: (for an active (not frozen or invoiced) milestone, the change simply applies as a non-billing-affecting change)
        Generally, what needs to happen is
            a) maintain state of what has been "locked in" on the invoice if that invoice has been frozen or sent out already and
            b) capture any changes coming in from fogbugz
        and then provide some tools for the user to resolve the differences. The rub is that each different kind of difference requires a different approach. Each
        difference, if not resolved, is a conflict. A list of conflicts is available to the user.
        New or Resolved/Closed Case
            A new case on or resolving an active case on a frozen milestone should have its milestone_excluded flag set.
            The user can decide whether to include it or not.
            Including the case resets the flag, requiring the following actions:
                1) if not resolved or closed, work to continue on the milestone to close the new case and a sync to update the status
                2) if the invoice has been sent, the corrected invoice to be resent
            If the user chooses to not include it, it remains in conflict.
        Reopened Case
            A reopened case on a frozen or invoiced milestone should have that active status recorded but remain resolved or closed and included in the milestone.
            Add "actual_status" and "conflicted" columns to case.
                a) frozen ->
                b) invoiced ->
            4) change to resolved user with a different rate
                a) frozen ->
                b) invoiced ->
            5) changed milestone to/from one that is frozen or invoiced
                a) frozen ->
                b) invoiced ->
        '''

        # - case isn't closed but we have it in the system, means it was closed before and reopened -or- we ran outside of 'billing only' previously
        # -- TODO: rather than prune out cases based on whether we're billing or not, take and keep everything and factor in status during cost calculation
        if app.config['FOGBUGZ_SYNC_BILLING_ONLY'] and not resolved_or_closed and fb_case:
            logger.warn("Case %s found in database but not resolved or closed (current status %s)" % (c.ixbug.string, c.sStatus.string))
            if milestone_frozen_and_invoiced:
                logger.warn("  - milestone frozen" % c.ixbug.string)
            if not milestone_frozen_and_invoiced and not app.config['FOGBUGZ_SYNC_CAREFUL']:
                # - in any case, the case isn't resolved or closed, so it doesn't belong here
                logger.warn("  - possible deletion" % c.ixbug.string)
                #g.db.delete(fb_case)
                #g.db.commit()

        if not resolved_or_closed and app.config['FOGBUGZ_SYNC_BILLING_ONLY']:
            logger.info("Case %s not resolved or closed - skipping" %(c.ixbug.string))
            continue

        if not milestone and app.config['FOGBUGZ_SYNC_BILLING_ONLY']:
            logger.info("No milestone found for case %s, cannot bill - skipping" % c.ixbug.string)
            continue

        resolving_person_id = int(c.ixPersonResolvedBy.string)
        assigned_person_id = int(c.ixPersonAssignedTo.string)
        resolving_person = None
        assigned_person = None
        resolving_fogbugz_user = None
        assigned_fogbugz_user = None

        if resolving_person_id > 0:
            resolving_person = fogbugz_client.get_person(resolving_person_id)
            resolving_fogbugz_user = g.db.query(FogbugzUser).filter(FogbugzUser.ixperson==resolving_person_id).first()
        if assigned_person_id > 0:
            assigned_person = fogbugz_client.get_person(assigned_person_id)
            assigned_fogbugz_user = g.db.query(FogbugzUser).filter(FogbugzUser.ixperson==assigned_person_id).first()

        if not resolving_person and app.config['FOGBUGZ_SYNC_BILLING_ONLY']:
            logger.info("Case %s resolved or closed by UNKNOWN entity (%s), cannot bill - skipping" %(c.ixbug.string, resolving_person_id))
            continue

        # -- someone resolved the case but that someone isn't tracked in our database yet
        if not resolving_fogbugz_user and resolving_person_id > 0:
            logger.warn("Resolving person on case but not found in DB..")
            fullname = resolving_person.sFullName.string if resolving_person else "DNE"
            resolving_fogbugz_user = FogbugzUser(ixperson=resolving_person_id, sfullname=fullname)
            add_object(resolving_fogbugz_user)
            logger.warn("Added new FogBugz user %s" % resolving_fogbugz_user.sfullname)

        if not assigned_fogbugz_user and assigned_person_id > 0:
            logger.warn("Assigned person on case but not found in DB..")
            fullname = assigned_person.sFullName.string if assigned_person else "DNE"
            assigned_fogbugz_user = FogbugzUser(ixperson=assigned_person_id, sfullname=fullname)
            add_object(assigned_fogbugz_user)
            logger.warn("Added new FogBugz user %s" % assigned_fogbugz_user.sfullname)

        # -- we have a rate for the resolving person stored from a previous run and the config rates table has changed since
        if resolving_fogbugz_user and resolving_fogbugz_user.sfullname in rates and float(resolving_fogbugz_user.frate) != float(rates[resolving_fogbugz_user.sfullname]):

            if milestone_frozen_and_invoiced and (app.config['FOGBUGZ_SYNC_BILLING_ONLY'] or app.config['FOGBUGZ_SYNC_CAREFUL']):
                logger.warn("Case-Resolving User's rate changed on frozen milestone!")
            else:
                logger.warn("%s got a raise from %.2f to %.2f" %(resolving_fogbugz_user.sfullname, float(resolving_fogbugz_user.frate), float(rates[resolving_fogbugz_user.sfullname])))
                resolving_fogbugz_user.frate = float(rates[resolving_fogbugz_user.sfullname])
                add_object(resolving_fogbugz_user)

        if fb_case:

            if fb_case.stitle != c.sTitle.string \
                or fb_case.ixfixfor != int(c.ixFixFor.string) \
                or fb_case.scategory != c.sCategory.string \
                or fb_case.sstatus != c.sStatus.string \
                or fb_case.sticket != c.sTicket.string \
                or (assigned_person_id > 0 and fb_case.ixpersonassignedto != assigned_person_id) \
                or (resolving_person_id > 0 and fb_case.ixpersonresolvedby != resolving_person_id):

                if fb_case.stitle != c.sTitle.string:
                    logger.info("Case %s title changed on frozen milestone (%s -> %s)" %(fb_case.ixbug, fb_case.stitle, c.stitle.string))
                    fb_case.stitle = c.stitle.string

                if fb_case.scategory != c.sCategory.string:
                    logger.info("Case %s category changed (%s -> %s)" %(fb_case.ixbug, fb_case.scategory, c.sCategory.string))
                    fb_case.scategory != c.sCategory.string

                if fb_case.sticket != c.sTicket.string:
                    logger.info("Case %s ticket changed (%s -> %s)" %(fb_case.ixbug, fb_case.sticket, c.sTicket.string))
                    fb_case.sticket = c.sTicket.string

                if fb_case.ixpriority != int(c.ixPriority.string):
                    fb_case.ixpriority = int(c.ixPriority.string)

                if fb_case.sstatus != c.sStatus.string or fb_case.ixfixfor != int(c.ixFixFor.string):
                    # - compare source and destination statuses
                    is_resolving_or_closing = not is_resolved_or_closed(fb_case.sstatus) and is_resolved_or_closed(c.sStatus.string)
                    is_reactivating = is_resolved_or_closed(fb_case.sstatus) and not is_resolved_or_closed(c.sStatus.string)
                    # - is the destination milestone frozen?
                    destination_milestone = g.db.query(Milestone).filter(Milestone.ixfixfor==int(c.ixFixFor.string)).first()
                    destination_milestone_frozen = destination_milestone.bfrozen and destination_milestone.binvoiced

                    # - if the status change affects how it interacts with billing and the milestone is frozen, exclude it
                    # - note this is a two-way move, it can be "included" if moving
                    fb_case.milestone_excluded = (is_resolving_or_closing or is_reactivating) and destination_milestone_frozen

                    if fb_case.ixfixfor != int(c.ixFixFor.string):
                        logger.info("Case %s milestone changed (%s -> %s)" %(fb_case.ixbug, fb_case.ixfixfor, c.ixFixFor.string))
                        fb_case.ixfixfor = int(c.ixFixFor.string)
                    if fb_case.sstatus != c.sStatus.string:
                        logger.info("Case %s status changed (%s -> %s)" %(fb_case.ixbug, fb_case.sstatus, c.sStatus.string))
                        fb_case.sstatus = c.sStatus.string

                if (assigned_person_id > 0 and fb_case.ixpersonassignedto != assigned_person_id):
                    logger.info("Case %s assignee changed (%s -> %s)" %(fb_case.ixbug, fb_case.ixpersonassignedto, assigned_person_id))

                if (resolving_person_id > 0 and fb_case.ixpersonresolvedby != resolving_person_id):
                    logger.info("Case %s resolver changed (%s -> %s)" %(fb_case.ixbug, fb_case.ixpersonresolvedby, resolving_person_id))

                if not (milestone_frozen_and_invoiced and app.config['FOGBUGZ_SYNC_CAREFUL']):

                    fb_case.update(
                        sTitle=c.sTitle.string,
                        ixpriority=int(c.ixPriority.string),
                        sstatus=c.sStatus.string,
                        scategory=c.sCategory.string,
                        sticket=c.sTicket.string,
                        ixfixfor=int(c.ixFixFor.string))

                    if assigned_person_id > 0:
                        fb_case.update(ixpersonassignedto=assigned_person_id)
                    else:
                        fb_case.update(ixpersonassignedto=None)

                    if resolving_person_id > 0:
                        fb_case.update(ixpersonresolvedby=resolving_person_id)
                    else:
                        fb_case.update(ixpersonresolvedby=None)

                    add_object(fb_case)

        else:
            if milestone.bfrozen:
                logger.warn("New Case %s (%s) added to frozen milestone '%s'" % (c.ixbug.string, c.stitle.string, milestone.sfixfor))
            fb_case = Case(
                int(c.ixBug.string),
                int(milestone.ixfixfor),
                c.sTitle.string,
                int(c.ixPriority.string),
                c.sStatus.string,
                c.sCategory.string,
                c.sTicket.string)
            fb_case.ixpersonresolvedby = resolving_person_id if resolving_person else None
            fb_case.milestone_excluded = milestone.bfrozen
            add_object(fb_case)

        resolving_user_case = None
        assigned_user_case = None
        # - if the case has a resolving user, that user gets all the credit
        # - but otherwise, at least attribute elapsed time to the assigned user
        user_cases = g.db.query(FogbugzUserCase).filter(FogbugzUserCase.ixbug==int(fb_case.ixbug))
        found_resolving_user_case = False
        found_assigned_user_case = False
        for user_case in user_cases:
            # - fogbugz itself does not track hours per user per case, only irrespective of user
            # - so we can expand on the model here but it doesn't mean much
            # - limit FogbugzUserCase count to one per case

            # - attribute all elapsed time to the user case that represents the current status
            if user_case.status == c.sStatus.string:
                user_case.fhours = float(c.hrsElapsed.string)
            else:
                user_case.fhours = 0
            if user_case.status == 'Resolved' or user_case.status == 'Closed':
                user_case.ixperson = int(resolving_fogbugz_user.ixperson)
                found_resolving_user_case = True
            else:
                user_case.ixperson = int(assigned_fogbugz_user.ixperson)
                found_assigned_user_case = True
            g.db.commit()

        if milestone_frozen_and_invoiced:
            logger.info("New FogbugzUserCase %s added to case in frozen milestone" %(fb_case.ixbug))
        if not (milestone_frozen_and_invoiced and app.config['FOGBUGZ_SYNC_CAREFUL']):
            if resolving_fogbugz_user and not found_resolving_user_case:
                resolving_user_case = FogbugzUserCase(status=fb_case.sstatus, ixperson=resolving_fogbugz_user.ixperson, ixbug=fb_case.ixbug, fhours=float(c.hrsElapsed.string))
                add_object(resolving_user_case)
            if assigned_fogbugz_user and not found_assigned_user_case:
                assigned_user_case = FogbugzUserCase(status=fb_case.sstatus, ixperson=assigned_fogbugz_user.ixperson, ixbug=fb_case.ixbug, fhours=float(c.hrsElapsed.string))
                add_object(assigned_user_case)

        events_results = fogbugz_client.search(q=fb_case.ixbug, cols="events")
        events = events_results.findAll("event")
        for event in events:
            db_event = g.db.query(CaseEvent).filter(CaseEvent.ixbugevent==event.ixBugEvent.string).first()
            # -- if ixpersonassignedto is on the event and it would change what's in the database, we need to make sure the person
            if int(event.ixPersonAssignedTo.string) > 0 and (not db_event or db_event.ixpersonassignedto != int(event.ixPersonAssignedTo.string)):
                assigned_person = g.db.query(FogbugzUser).filter(FogbugzUser.ixperson==event.ixPersonAssignedTo.string).first()
                if not assigned_person:
                    assigned_person_user = fogbugz_client.get_person(int(event.ixPersonAssignedTo.string))
                    logger.info("  Adding assigned person (%s - %s)" % (event.ixPersonAssignedTo.string, assigned_person_user.sFullName.string))
                    assigned_person = FogbugzUser(ixperson=event.ixPersonAssignedTo.string, sfullname=assigned_person_user.sFullName.string)
                    add_object(assigned_person)
            if db_event:
                if db_event.sverb != event.sVerb.string or db_event.evtdescription != event.evtDescription.string or (event.shtml is not None and db_event.shtml != event.shtml.string) or (event.shtml is None and db_event.shtml is not None):
                    logger.info("  Case event %s has changed" % event.ixBugEvent.string)
                    db_event.update(sverb=event.sVerb.string, evtdescription=event.evtDescription.string, shtml=event.shtml.string)
                    g.db.commit()
                if not db_event.ixpersonassignedto and int(event.ixPersonAssignedTo.string) > 0:
                    logger.info("  Case event %s getting its ixpersonassignedto fixed" % event.ixBugEvent.string)
                    db_event.update(ixpersonassignedto=event.ixPersonAssignedTo.string)
                    g.db.commit()
            else:
                logger.debug("  Case event %s to be added" % event.ixBugEvent.string)
                acting_person = g.db.query(FogbugzUser).filter(FogbugzUser.ixperson==event.ixPerson.string).first()
                if not acting_person:
                    logger.info("  Adding acting person (%s - %s)" % (event.ixPerson.string, event.sPerson.fullname))
                    acting_person = FogbugzUser(ixperson=event.ixPerson.string, sfullname=event.sPerson.string)
                    add_object(acting_person)
                db_event = CaseEvent(
                    ixbug=c.ixBug.string,
                    ixbugevent=event.ixBugEvent.string,
                    sverb=event.sVerb.string,
                    ixperson=event.ixPerson.string)
                if int(event.ixPersonAssignedTo.string) > 0:
                    db_event.ixpersonassignedto = event.ixPersonAssignedTo.string
                db_event.dt = event.dt.string
                db_event.evtdescription = event.evtDescription.string
                if event.shtml is not None:
                    db_event.shtml = event.shtml.string
                add_object(db_event)

if __name__ == "__main__":

    try:

        logger = get_logger()
        from webapp.invoicing.fogbugz_client import FogBugzClient
        from utilities.data_pull import refresh

        fbc = FogBugzClient()

        if not fbc.test_connection():
            raise Exception("Failed to get a FogBugz client going")

        from multiprocessing import Process

        with app.app_context():
            from webapp import connect_db
            g.db = connect_db()
            #refresh(fogbugz_client=fbc)
            p = Process(target=refresh, args=(fbc, None, logger,))
            p.start()
            p.join()

    except:
        logger.error(str(sys.exc_info()[0]))
        logger.error(str(sys.exc_info()[1]))
        traceback.print_tb(sys.exc_info()[2])
