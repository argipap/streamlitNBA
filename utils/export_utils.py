# Download NBA player stats data
import base64


class ExportUtils:
    # https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
    # Download and export to CSV
    @classmethod
    def export_to_csv(cls, df, stats_category, year):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" \
        download="playerstats_{stats_category}_{year}.csv">Download CSV File</a>'
        return href
