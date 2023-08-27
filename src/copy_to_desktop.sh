#!/bin/bash

ZIPNAME="mauna_system_report.tar.gz";
if [ $LANG == "pt_BR.UTF-8" ]; then
    ZIPNAME="relatorio_do_sistema_mauna.tar.gz";
elif [ $LANG == "pt_PT.UTF-8" ]; then
    ZIPNAME="relatorio_do_sistema_mauna.tar.gz";
elif [ $LANG == "af.UTF-8" ]; then
    ZIPNAME="mauna_stelselverslag.tar.gz";    
elif [ $LANG == "ar.UTF-8" ]; then
    ZIPNAME="تقرير_نظام_ماونا.tar.gz";
elif [ $LANG == "da.UTF-8" ]; then
    ZIPNAME="mauna_system_rapport.tar.gz";    
elif [ $LANG == "de.UTF-8" ]; then
    ZIPNAME="mauna_Systembericht.tar.gz";
elif [ $LANG == "el.UTF-8" ]; then
    ZIPNAME="αναφορά_συστήματος_mauna.tar.gz";    
elif [ $LANG == "es.UTF-8" ]; then
    ZIPNAME="informe_del_sistema_mauna.tar.gz";
elif [ $LANG == "fi.UTF-8" ]; then
    ZIPNAME="mauna_järjestelmäraportti.tar.gz";    
elif [ $LANG == "fr.UTF-8" ]; then
    ZIPNAME="rapport_systeme_mauna.tar.gz";
elif [ $LANG == "he.UTF-8" ]; then
    ZIPNAME="דוח_מערכת_מאונה.tar.gz";
elif [ $LANG == "hi.UTF-8" ]; then
    ZIPNAME="मौना_सिस्टम_रिपोर्ट.tar.gz";
elif [ $LANG == "id.UTF-8" ]; then
    ZIPNAME="laporan_sistem_mauna.tar.gz"; 
elif [ $LANG == "it.UTF-8" ]; then
    ZIPNAME="rapporto_sul_sistema_mauna.tar.gz";  
elif [ $LANG == "ja.UTF-8" ]; then
    ZIPNAME="マウナシステムレポート.tar.gz";   
elif [ $LANG == "ko.UTF-8" ]; then
    ZIPNAME="마우나_시스템_보고서.tar.gz";
elif [ $LANG == "nl.UTF-8" ]; then
    ZIPNAME="mauna_systeemrapport.tar.gz"; 
elif [ $LANG == "no.UTF-8" ]; then
    ZIPNAME="mauna_systemrapport.tar.gz";
elif [ $LANG == "pl.UTF-8" ]; then
    ZIPNAME="raport_systemu_mauna.tar.gz";  
elif [ $LANG == "ro.UTF-8" ]; then
    ZIPNAME="raport_sistem_mauna.tar.gz"; 
elif [ $LANG == "ru.UTF-8" ]; then
    ZIPNAME="системный_отчет_мауна.tar.gz"; 
elif [ $LANG == "sv.UTF-8" ]; then
    ZIPNAME="mauna_system_rapport.tar.gz"; 
elif [ $LANG == "th.UTF-8" ]; then
    ZIPNAME="รายงานระบบเมาน่า.tar.gz";                                        
elif [ $LANG == "tr_TR.UTF-8" ]; then
    ZIPNAME="mauna_sistem_raporu.tar.gz";
elif [ $LANG == "uk.UTF-8" ]; then
    ZIPNAME="системний_звіт_mauna.tar.gz";    
elif [ $LANG == "vi.UTF-8" ]; then
    ZIPNAME="báo_cáo_hệ_thống_mauna.tar.gz"; 
elif [ $LANG == "zh_CN.UTF-8" ]; then
    ZIPNAME="莫纳系统报告.tar.gz"; 
elif [ $LANG == "zh_HK.UTF-8" ]; then
    ZIPNAME="莫納系統報告.tar.gz";
elif [ $LANG == "zh_MO.UTF-8" ]; then
    ZIPNAME="莫納系統報告.tar.gz";    
elif [ $LANG == "zh_TW.UTF-8" ]; then
    ZIPNAME="莫納系統報告.tar.gz";              
fi

desktop=$(xdg-user-dir DESKTOP);
cp /tmp/$ZIPNAME "$desktop"
