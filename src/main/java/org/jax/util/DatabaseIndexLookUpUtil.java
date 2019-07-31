package org.jax.util;

import org.springframework.jdbc.core.JdbcTemplate;

public class DatabaseIndexLookUpUtil {
    /**
     * Check whether an index is already present on a table.
     * refer to: https://stackoverflow.com/questions/2480148/how-can-i-employ-if-exists-for-creating-or-dropping-an-index-in-mysql
     */
    public static boolean indexExists(String tablename, String indexname, JdbcTemplate jdbcTemplate){
        Integer count = jdbcTemplate.queryForObject("select count(*) from information_schema.statistics where table_name = ? and index_name = ? and table_schema = database()", new String[]{tablename, indexname}, Integer.class);
        return count != null && count > 0;
    }

}
