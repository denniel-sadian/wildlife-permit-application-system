# Generated by Django 4.1.7 on 2023-09-23 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0027_alter_collectionentry_permit_application'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requirement',
            name='requirement_type',
            field=models.CharField(choices=[('PRIOR_CLEARANCE_FROM_AFFECTED_COMMUNITIES', 'Prior clearance from the affected communities, i.e. concerned LGUs, recognized head people in accordance with R.A. 8371, or PAMB'), ('CERT_OF_REGISTRATION', 'Copy of Certificate of Registration from appropriate Government agencies'), ('SCIENTIFIC_EXPERTISE_PROOF', 'Proof of scientific expertise (list of qualifications of manpower)'), ('FINANCIAL_PLAN', 'Financial plan showing financial capability to go into breeding'), ('PROPOSED_FACILITY_DESIGN', 'Proposed facility design'), ('LETTER_OF_COMMITMENT', 'In case of indigenous threatened species, letter of commitment to simultaneously undertake conservation breeding and propose measures on rehabilitation and/or protection of habitat, where appropriate, as may be determined by the RWMC'), ('CITIZENSHIP', 'Citizenship verification papers, if citizenship is by Naturalization'), ('DOCUMENTS_SUPPORTING_LEGAL_POSSESSION_OF_WILDLIFE', 'Documents supporting the legal possession/ acquisition of wildlife'), ('PHYTOSANITARY_OR_VETERINARY_CERT', 'Phytosanitary Certificate (for plants) or Veterinary Quarantine Certificate (for animals) from the concerned Department of Agriculture (DA) Office.'), ('ACQUISITION_PROOF_OR_DEEDS_OF_DONATION', 'Proof of Acquisition/Deeds of Donation'), ('ENDORSEMENT_LETTER', 'Endorsement letter from dead/recognized expert/conservation organization'), ('COPY_OF_RESEARCH_THESIS_DISSERTATION', 'Copy of the research/thesis/dissertation proposals, or copy of the affidavit of undertaking/approved memorandum of agreement (MOA)')], max_length=50),
        ),
        migrations.AlterField(
            model_name='requirementitem',
            name='requirement',
            field=models.CharField(choices=[('PRIOR_CLEARANCE_FROM_AFFECTED_COMMUNITIES', 'Prior clearance from the affected communities, i.e. concerned LGUs, recognized head people in accordance with R.A. 8371, or PAMB'), ('CERT_OF_REGISTRATION', 'Copy of Certificate of Registration from appropriate Government agencies'), ('SCIENTIFIC_EXPERTISE_PROOF', 'Proof of scientific expertise (list of qualifications of manpower)'), ('FINANCIAL_PLAN', 'Financial plan showing financial capability to go into breeding'), ('PROPOSED_FACILITY_DESIGN', 'Proposed facility design'), ('LETTER_OF_COMMITMENT', 'In case of indigenous threatened species, letter of commitment to simultaneously undertake conservation breeding and propose measures on rehabilitation and/or protection of habitat, where appropriate, as may be determined by the RWMC'), ('CITIZENSHIP', 'Citizenship verification papers, if citizenship is by Naturalization'), ('DOCUMENTS_SUPPORTING_LEGAL_POSSESSION_OF_WILDLIFE', 'Documents supporting the legal possession/ acquisition of wildlife'), ('PHYTOSANITARY_OR_VETERINARY_CERT', 'Phytosanitary Certificate (for plants) or Veterinary Quarantine Certificate (for animals) from the concerned Department of Agriculture (DA) Office.'), ('ACQUISITION_PROOF_OR_DEEDS_OF_DONATION', 'Proof of Acquisition/Deeds of Donation'), ('ENDORSEMENT_LETTER', 'Endorsement letter from dead/recognized expert/conservation organization'), ('COPY_OF_RESEARCH_THESIS_DISSERTATION', 'Copy of the research/thesis/dissertation proposals, or copy of the affidavit of undertaking/approved memorandum of agreement (MOA)')], max_length=1000),
        ),
    ]
