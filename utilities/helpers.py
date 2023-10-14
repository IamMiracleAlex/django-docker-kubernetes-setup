from datetime import timedelta

from django.utils import timezone
from django.db.models.query import QuerySet
from django.http import  HttpResponse

from utilities.api_response import APIFailure


class ExportItem:
    def __init__(self, data, caption: str = 'Reports data', fields: list = []):
        '''
        This class creates reports
        Args:
            data: a list of dictionaries, or a queryset
            caption: a string to caption report
            fields: the fields of the model
        '''
        self.caption = caption


        if len(data) == 0:
        	raise ValueError('Data must not be empty')
			
        if isinstance(data, list):
        	self.data = data
        elif isinstance(data, QuerySet):
        	self.data = data.values()
        else: 
        	raise ValueError('Data must be a list or queryset')
		
        if fields:
        	for x in fields:
        		if not x in self.data[0].keys():
        			raise AttributeError(f'This field: {x} is not a valid field')
        	self.fields = fields
        else: 
        	self.fields = self.data[0].keys()
			
		
    def export_to_html(self):
        '''
        Writes the html string to a html file
        '''

        # Save the HTML code
        path = 'report.html'
        content = self.create_html_data()

        file_obj = open(path, 'w')
        file_obj.write(content)
        file_obj.close()

        download_file = open(path)

        response =  HttpResponse(content=download_file, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="{path}"'
        return response


    def format_tile(self, value) -> str:
        '''
        Format the title in a good form, 
		Converts first_name -> First Name
        '''

        new_val = value.split('_')
        return " ".join([x.capitalize() for x in new_val])
     

    def create_html_data(self):
        '''
        Creates html data for reports
        '''

        # Start the page
        content = '''
        <html>
            <head>
            <title>''' + self.caption + '''</title> 
            </head>  
            <body>
                <center>
            \n
        '''

        # Add content to the body
        # content += self.create_html_table()
        content += "<table style='border:1px solid black; '>\n"
        content += "<caption style='font-weight: bold; font-size: 10px; padding-top: 3px;' >" + self.caption + "</caption>\n"
        content += '<tr>\n'

        for k in self.fields:
            content += "<th style='padding-top: 3px;' >" + self.format_tile(k) + '</th>'
        content += '</tr>\n'

        content += "  <tr>\n"
        for row in self.data:
            for k in self.fields:
                content += "<td style='padding-top: 3px;' >" + str(row[k]) + "</td>\n"
            content += '</tr>\n'

        content += '\t</table>\n'

        # Close the body and end the file
        content += '''  
            </center>
            </body>
        </html>
        '''
        return content

		
    def export_to_pdf(self):
        '''
        exports html string to pdf
        '''
        from xhtml2pdf import pisa
           
        content = self.create_html_data()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        pisa_status = pisa.CreatePDF(content, dest=response)
	
        if pisa_status.err:
            return APIFailure(message=f'We had some errors {pisa_status.err}')
                
        return response	


    def export_to_csv(self):
        '''
        export items to csv
        '''
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow(self.fields)
        [writer.writerow([obj.get(field) for field in self.fields]) for obj in self.data]

        return response	
  
		
    def export_to_excel(self):
        '''
        export items to excel
        '''
        import pandas as pd

        path = 'report.xlsx'
        df = pd.DataFrame.from_records(self.data, columns=self.fields)
        df.to_excel(path)
        file_obj = open(path, 'rb').read()
		
        response = HttpResponse(content=file_obj, content_type='mimetype/submimetype')
        response['Content-Disposition'] = 'attachment; filename=report.xlsx'	

        return response


    def export(self, file_type):
        '''
        export items to csv, html, or pdf
        '''
        
        if not file_type in ['csv', 'excel', 'pdf', 'html']:
        	raise TypeError('The acceptable file types are: csv, excel, pdf, html')

        exports = {
			'csv': self.export_to_csv,
			'excel': self.export_to_excel,
			'html': self.export_to_html,
			'pdf': self.export_to_pdf,
		}
        return exports.get(file_type)()


def last_n_days_ago(n: int):
    return timezone.now().date() - timedelta(days=n)