CREATE OR REPLACE PROCEDURE main.erraudit_demo_sm(
	)
LANGUAGE 'plpgsql'
    SECURITY DEFINER 
AS $BODY$
DECLARE
BEGIN
delete from finvchdet where vchcode = 22559;
END;
$BODY$;

