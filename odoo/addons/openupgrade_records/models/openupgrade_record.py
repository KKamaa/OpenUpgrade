# coding: utf-8
# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Attribute(models.Model):
    _name = 'openupgrade.attribute'
    _description = 'OpenUpgrade Attribute'

    name = fields.Char(readonly=True)
    value = fields.Char(readonly=True)
    record_id = fields.Many2one(
        'openupgrade.record', ondelete='CASCADE',
        readonly=True,)


class Record(models.Model):
    _name = 'openupgrade.record'
    _description = 'OpenUpgrade Record'

    name = fields.Char(readonly=True)
    module = fields.Char(readonly=True)
    model = fields.Char(readonly=True)
    field = fields.Char(readonly=True)
    mode = fields.Selection(
            [('create', 'Create'), ('modify', 'Modify')],
            help='Set to Create if a field is newly created '
            'in this module. If this module modifies an attribute of an '
            'existing field, set to Modify.',
            readonly=True)
    type = fields.Selection(  # Uh oh, reserved keyword
            [('field', 'Field'), ('xmlid', 'XML ID')],
            readonly=True)
    attribute_ids = fields.One2many(
            'openupgrade.attribute', 'record_id',
            readonly=True)
    noupdate = fields.Boolean(readonly=True)
    prefix = fields.Char(compute='_compute_prefix_and_suffix')
    suffix = fields.Char(compute='_compute_prefix_and_suffix')
    original_module = fields.Char(compute='_compute_original_module')

    @api.depends('name')
    def _compute_prefix_and_suffix(self):
        for rec in self:
            rec.prefix, rec.suffix = rec.name.split('.', 1)

    @api.depends('model')
    def _compute_original_module(self):
        for rec in self:
            rec.original_module = self.env[rec.model]._original_module

    @api.model
    def field_dump(self):
        keys = [
            'attachment',
            'module',
            'mode',
            'model',
            'field',
            'type',
            'isfunction',
            'isproperty',
            'isrelated',
            'relation',
            'required',
            'stored',
            'selection_keys',
            'req_default',
            'inherits',
            ]

        template = dict([(x, False) for x in keys])
        data = []
        for record in self.search([('type', '=', 'field')]):
            repre = template.copy()
            repre.update({
                'module': record.module,
                'model': record.model,
                'field': record.field,
                'mode': record.mode,
                })
            repre.update(
                dict([(x.name, x.value) for x in record.attribute_ids]))
            data.append(repre)
        return data
