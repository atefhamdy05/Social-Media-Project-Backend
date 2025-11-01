from .executor import execute_query
from concurrent.futures import ThreadPoolExecutor


def fetch_customers(search):
    query = """
    SELECT
        CUST_NAME,
        CUST_NO AS CIF_ID,
        CUST_ID AS ID_NO,
        CONTACT_NO_1 AS MOBILE,
        APPL_ID,
        BUCKET,
        CITY_AR,
        DOB_DOI,
        EMAIL_ID,
        SUM(OS) AS OS,
        SUM(OVERDUE_AMNT) AS OVERDUE_AMNT,
        MAX(TENURE) AS TENURE,
        MAX(DPD) AS DPD,
        SUM(EMI) AS EMI,
        SUM(TOTAL_PAID) AS TOTAL_PAID,
        SUM(EXCESS_AMOUNT) AS EXCESS_AMOUNT,
        MIN(NEXT_DUE_DATE_EMI) AS NEXT_DUE_DATE_EMI,
        SUM(NEXT_DUE_AMNT) AS NEXT_DUE_AMNT,
        A.SUB_STAT,
        count(*) total_agr,
        A.MAIN_STAT
    FROM SIR_AGR_DTLS_KSL_WEB_V@PROD_BRIDGE A, SIR_CIF_CUSTOMER_DTL@PROD_BRIDGE B
    WHERE A.CUST_NO = B.CIF_ID AND 
    (
        CONTACT_NO_1 = :search
        OR CUST_NO   = :search
        OR APPL_ID   = :search
    )
    GROUP BY 
        CUST_NAME,
        CUST_NO,
        CUST_ID,
        APPL_ID,
        CONTACT_NO_1,
        BUCKET,
        CITY_AR,
        DOB_DOI,
        EMAIL_ID,
        A.SUB_STAT,
        A.MAIN_STAT
"""
    return execute_query(query, params={"search":search}, fetch_size=1) 


def fetch_regions_drop_down():
    query = '''
        SELECT DISTINCT REGION_AR FROM SIR_REP_FIN_SALES_V@PROD_BRIDGE WHERE REGION_AR IS NOT NULL
    '''
    return execute_query(query)

def fetch_buckets_drop_down():
    query = '''
        SELECT * FROM SIR_MTM_BUCKET@PROD_BRIDGE
    '''
    return execute_query(query)

def fetch_customer_categories_drop_down():
    query = '''
        SELECT DISTINCT CUSTOMER_CATEGORY FROM SIR_CIF_CUSTOMER_DTL@PROD_BRIDGE WHERE CUSTOMER_CATEGORY IS NOT NULL
    '''
    return execute_query(query)



def fetch_advanced_search_customers(params):
    query = '''
        SELECT 
            CUST_NAME,
            CUST_NO,
            ID_NO,
            MOBILE,
            APPL_ID,
            BUCKET,
            REGION_AR,
            DOB_DOI,
            EMAIL_ID,
            OS,
            OVERDUE_AMNT,
            TENURE,
            DPD,
            EMI,
            TOTAL_PAID,
            EXCESS_AMOUNT,
            NEXT_DUE_DATE_EMI,
            NEXT_DUE_AMNT,
            SUB_STAT,
            MAIN_STAT
        FROM SIR_AGR_DTLS_KSL_WEB_V@PROD_BRIDGE A
        JOIN SIR_CIF_CUSTOMER_DTL@PROD_BRIDGE B
            ON A.CUST_NO = B.CIF_ID 
        WHERE 
            A.BUCKET LIKE '%' || :bucket  || '%'
            AND A.REGION_AR LIKE '%' || :region || '%'
            AND B.CUSTOMER_CATEGORY  LIKE '%' || :customer_category || '%'
            
            AND rownum < 10
    '''

    return execute_query(query, params=params)

def fetch_send_advanced_search_customers(params):
    query = '''
        SELECT 
            CIF_ID, 
            CUSTOMER_NAME, 
            CUSTOMER_NAME_AR, 
            ID_NO,
            MOBILE
        FROM SIR_AGR_DTLS_KSL_WEB_V@PROD_BRIDGE A
        JOIN SIR_CIF_CUSTOMER_DTL@PROD_BRIDGE B
            ON A.CUST_NO = B.CIF_ID  
        WHERE 
            A.BUCKET LIKE '%' || :bucket  || '%'
            AND A.REGION_AR LIKE '%' || :region || '%'
            AND B.CUSTOMER_CATEGORY  LIKE '%' || :customer_category || '%'                   
    '''
    return execute_query(query, params=params)

def get_customer_base_data_by_cif_ids(cif_ids:list):
    cif_ids =  ', '.join(cif_ids)

    query = f'''
        SELECT 
            CIF_ID, 
            CUSTOMER_NAME, 
            CUSTOMER_NAME_AR, 
            ID_NO,
            MOBILE
        FROM 
        SIR_CIF_CUSTOMER_DTL@PROD_BRIDGE WHERE CIF_ID IN ({cif_ids})                 
    '''
    return execute_query(query)




def get_customer_advanced_search_drop_downs():
    with ThreadPoolExecutor() as executor:
        future_regions      = executor.submit(fetch_regions_drop_down)
        future_buckets      = executor.submit(fetch_buckets_drop_down)
        future_categories   = executor.submit(fetch_customer_categories_drop_down)

        # wait for all to finish
        regions_drop_down               = future_regions.result()
        buckets_drop_down               = future_buckets.result()
        customer_categories_drop_down   = future_categories.result()

    error = regions_drop_down['error'] or buckets_drop_down['error'] or customer_categories_drop_down['error']
    if error:
        return None, error
    
    return {
        'regions'               : regions_drop_down['data'],
        'buckets'               : buckets_drop_down['data'],
        'customer_categories'   : customer_categories_drop_down['data'],
    }, None


