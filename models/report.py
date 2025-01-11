import base64
from odoo import models
from datetime import datetime


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        res = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids)
        model_name = data['context']['active_model']

        # Save the PDF as an attachment for each res_id and post it to Chatter
        if res_ids:
            for res_id in set(res_ids):
                pdf_stream = res[res_id]['stream']
                # Reset the stream pointer to the beginning
                pdf_stream.seek(0)
                pdf_content = pdf_stream.read()
                record = self.env[model_name].browse(res_id)

                # Construct the attachment name
                attachment_name = f"{record.name}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"

                # Create the attachment
                attachment = self.env['ir.attachment'].create({
                    'name': attachment_name,
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'mimetype': 'application/pdf',
                    'res_model': model_name,
                    'res_id': res_id,
                })

                # Post the attachment to the Chatter
                record.message_post(
                    body=f"Generated report: {attachment_name}",
                    attachment_ids=[attachment.id],
                )

        return res

