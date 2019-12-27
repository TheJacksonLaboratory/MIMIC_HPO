package org.jax;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.PropertySource;

/**
 * @author Daniel Danis <daniel.danis@jax.org>
 * @author Aaron Zhang
 */
//@PropertySource("classpath:uniphenominer.properties")
//@ConfigurationProperties(prefix = "uniphenominer")
public class UniPhenominerProperties {

    private String dataDirectory;

    private String hpoOboFile;

    public String getHpoOboFile() {
        return hpoOboFile;
    }

    public void setHpoOboFile(String hpoOboFile) {
        this.hpoOboFile = hpoOboFile;
    }

    public String getDataDirectory() {
        return dataDirectory;
    }

    public void setDataDirectory(String dataDirectory) {
        this.dataDirectory = dataDirectory;
    }

    @Override
    public String toString() {
        return "UniPhenominerProperties{" +
                "dataDirectory='" + dataDirectory + '\'' +
                ", hpoOboFile='" + hpoOboFile + '\'' +
                '}';
    }
}
