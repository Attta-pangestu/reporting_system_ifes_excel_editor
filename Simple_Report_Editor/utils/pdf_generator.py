"""
PDF Generator Module
Convert Excel reports to PDF format
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import win32com.client as win32
import pythoncom

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Generator untuk mengkonversi Excel ke PDF"""

    def __init__(self):
        self.excel_app = None

    def _init_excel(self) -> bool:
        """
        Inisialisasi Excel application

        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            pythoncom.CoInitialize()
            self.excel_app = win32.Dispatch("Excel.Application")
            self.excel_app.Visible = False
            self.excel_app.DisplayAlerts = False
            logger.info("Excel application initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Excel: {e}")
            return False

    def _cleanup_excel(self):
        """Cleanup Excel application"""
        try:
            if self.excel_app:
                self.excel_app.Quit()
                self.excel_app = None
            pythoncom.CoUninitialize()
            logger.info("Excel application cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up Excel: {e}")

    def convert_to_pdf(self,
                      excel_path: str,
                      pdf_path: str = None,
                      settings: Dict[str, Any] = None) -> str:
        """
        Konversi file Excel ke PDF

        Args:
            excel_path: Path ke file Excel
            pdf_path: Path untuk output PDF (optional)
            settings: Konfigurasi PDF (optional)

        Returns:
            Path ke file PDF yang dihasilkan
        """
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        # Generate PDF path if not provided
        if pdf_path is None:
            base_name = os.path.splitext(os.path.basename(excel_path))[0]
            pdf_path = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # Ensure PDF path has .pdf extension
        if not pdf_path.lower().endswith('.pdf'):
            pdf_path += '.pdf'

        try:
            # Initialize Excel
            if not self._init_excel():
                raise Exception("Failed to initialize Excel application")

            # Open workbook
            logger.info(f"Opening Excel file: {excel_path}")
            workbook = self.excel_app.Workbooks.Open(os.path.abspath(excel_path))

            # Apply settings if provided
            if settings:
                self._apply_settings(workbook, settings)

            # Export to PDF
            logger.info(f"Converting to PDF: {pdf_path}")
            pdf_type = 0  # xlTypePDF
            quality = 0   # xlQualityStandard

            workbook.ExportAsFixedFormat(
                Type=pdf_type,
                Filename=os.path.abspath(pdf_path),
                Quality=quality,
                IncludeDocProperties=True,
                IgnorePrintAreas=False
            )

            # Close workbook
            workbook.Close(SaveChanges=False)

            logger.info(f"PDF created successfully: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"Error converting to PDF: {e}")
            raise
        finally:
            self._cleanup_excel()

    def _apply_settings(self, workbook, settings: Dict[str, Any]):
        """
        Apply pengaturan PDF ke workbook

        Args:
            workbook: Excel workbook object
            settings: Dictionary pengaturan
        """
        try:
            # Page setup settings
            for worksheet in workbook.Worksheets:
                page_setup = worksheet.PageSetup

                # Orientation
                orientation = settings.get('orientation', 'portrait')
                if orientation.lower() == 'landscape':
                    page_setup.Orientation = 2  # xlLandscape
                else:
                    page_setup.Orientation = 1  # xlPortrait

                # Paper size
                paper_size = settings.get('paper_size', 'A4')
                paper_sizes = {
                    'A4': 9,
                    'A3': 8,
                    'Letter': 1,
                    'Legal': 5
                }
                if paper_size in paper_sizes:
                    page_setup.PaperSize = paper_sizes[paper_size]

                # Margins (in points)
                margins = settings.get('margins', {})
                if 'top' in margins:
                    page_setup.TopMargin = self._cm_to_points(margins['top'])
                if 'bottom' in margins:
                    page_setup.BottomMargin = self._cm_to_points(margins['bottom'])
                if 'left' in margins:
                    page_setup.LeftMargin = self._cm_to_points(margins['left'])
                if 'right' in margins:
                    page_setup.RightMargin = self._cm_to_points(margins['right'])

                # Fit to page
                if settings.get('scale_to_fit', False):
                    page_setup.FitToPagesWide = 1
                    page_setup.FitToPagesTall = False

            # Header and footer
            header_text = settings.get('header_text', '')
            footer_text = settings.get('footer_text', '')

            for worksheet in workbook.Worksheets:
                page_setup = worksheet.PageSetup

                if header_text:
                    # Replace placeholders
                    processed_header = self._process_header_footer_text(header_text)
                    page_setup.CenterHeader = processed_header

                if footer_text:
                    # Replace placeholders
                    processed_footer = self._process_header_footer_text(footer_text)
                    page_setup.CenterFooter = processed_footer

        except Exception as e:
            logger.warning(f"Error applying PDF settings: {e}")

    def _cm_to_points(self, cm: float) -> float:
        """
        Konversi cm ke points (1 cm = 28.35 points)

        Args:
            cm: Value in centimeters

        Returns:
            Value in points
        """
        return cm * 28.35

    def _process_header_footer_text(self, text: str) -> str:
        """
        Process header/footer text dengan Excel formatting codes

        Args:
            text: Raw text dengan placeholders

        Returns:
            Processed text dengan Excel codes
        """
        # Replace common placeholders
        processed = text.replace('{page_num}', '&P')  # Page number
        processed = processed.replace('{total_pages}', '&N')  # Total pages
        processed = processed.replace('{date}', '&D')  # Current date
        processed = processed.replace('{time}', '&T')  # Current time
        processed = processed.replace('{file}', '&F')  # File name
        processed = processed.replace('{tab}', '&A')  # Sheet name

        # Add formatting if needed
        if '&&B' not in processed:  # Bold
            processed = f'&B{processed}'

        return processed

    def convert_batch_to_pdf(self,
                            excel_files: list,
                            output_dir: str = None,
                            settings: Dict[str, Any] = None) -> list:
        """
        Konversi multiple Excel files ke PDF

        Args:
            excel_files: List path file Excel
            output_dir: Directory output (optional)
            settings: Pengaturan PDF (optional)

        Returns:
            List path file PDF yang dihasilkan
        """
        pdf_files = []

        for excel_file in excel_files:
            try:
                if output_dir:
                    base_name = os.path.splitext(os.path.basename(excel_file))[0]
                    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
                else:
                    pdf_path = None

                pdf_file = self.convert_to_pdf(excel_file, pdf_path, settings)
                pdf_files.append(pdf_file)

            except Exception as e:
                logger.error(f"Error converting {excel_file}: {e}")
                pdf_files.append(None)

        return pdf_files

    def get_default_pdf_settings(self) -> Dict[str, Any]:
        """
        Get default PDF settings

        Returns:
            Dictionary default settings
        """
        return {
            'orientation': 'landscape',
            'paper_size': 'A4',
            'margins': {
                'top': 1.0,
                'bottom': 1.0,
                'left': 1.0,
                'right': 1.0
            },
            'scale_to_fit': True,
            'header_text': '&BReport Generated on &D',
            'footer_text': '&BPage &P of &N'
        }

    def validate_excel_file(self, excel_path: str) -> bool:
        """
        Validasi apakah file Excel bisa dibuka

        Args:
            excel_path: Path ke file Excel

        Returns:
            True jika valid, False jika tidak
        """
        try:
            if not os.path.exists(excel_path):
                return False

            if not self._init_excel():
                return False

            workbook = self.excel_app.Workbooks.Open(os.path.abspath(excel_path))
            workbook.Close(SaveChanges=False)

            return True

        except Exception as e:
            logger.error(f"Error validating Excel file: {e}")
            return False
        finally:
            self._cleanup_excel()

    def __del__(self):
        """Cleanup saat object dihapus"""
        self._cleanup_excel()