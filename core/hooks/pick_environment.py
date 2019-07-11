# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook which chooses an environment file to use based on the current context.
"""

from tank import Hook


class PickEnvironment(Hook):

    def execute(self, context, **kwargs):
        """
        The default implementation assumes there are three environments, called shot, asset
        and project, and switches to these based on entity type.
        """

        self.logger.debug(
            "Picking environment for Context %s: Project %s, Entity %s, Task %s, Source Entity %s" % (
                context,
                context.project,
                context.entity,
                context.task,
                context.source_entity
            )
        )

        me = context.sgtk.shotgun.find_one(
            "HumanUser",
            [["id", "is", context.user["id"]]],
            ["permission_rule_set.PermissionRuleSet.display_name"]
        )
        if me["permission_rule_set.PermissionRuleSet.display_name"] == "Vendor":
            if context.project is None:
                # this happens when Desktop boots against a project-independent config
                # but no project has been chosen yet
                self.logger.debug("Using site_vendor context")
                return "site_vendor"

            self.logger.debug("Using vendor context")
            return "vendor"

        # For testing vendor only, if the current pipeline config starts with "dev_vendor"
        # then return the vendor config
        if context.sgtk.pipeline_configuration.get_name().lower().startswith("dev_vendor"):
            if context.project is None:
                # this happens when Desktop boots against a project-independent config
                # but no project has been chosen yet
                self.logger.debug("Using site_vendor context")
                return "site_vendor"

            self.logger.debug("Using vendor context")
            return "vendor"

        if context.source_entity:
            if context.source_entity["type"] == "Version":
                return "version"
            elif context.source_entity["type"] == "PublishedFile":
                return "publishedfile"

        if context.project is None:
            # Our context is completely empty. We're going into the site context.
            return "site"

        if context.entity is None:
            # We have a project but not an entity.
            return "project"

        if context.entity and context.step is None:
            # We have an entity but no step.
            if context.entity["type"] == "Shot":
                return "shot"
            if context.entity["type"] == "Asset":
                return "asset"
            if context.entity["type"] == "Sequence":
                return "sequence"
            if context.entity["type"] == "Playlist":
                return "playlist"

        if context.entity and context.step:
            # We have a step and an entity.
            if context.entity["type"] == "Shot":
                return "shot_step"
            if context.entity["type"] == "Asset":
                return "asset_step"

        return None
