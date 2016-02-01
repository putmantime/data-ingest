import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import java.util.ArrayList;

public class ReadXMLFile {

    public static StringBuilder sb;
    public static ArrayList<Entry> entries = new ArrayList<Entry>();
    public static Entry entry;


    public static void main(String args[]) {

        parse();
        serialize();

    }

    private static void serialize() {
        StringBuilder allentries = new StringBuilder();
        for (Entry entry : entries) {
            allentries.append(entry);
        }
        System.out.println(allentries.toString());
    }

    public static void parse() {

        try {

            SAXParserFactory factory = SAXParserFactory.newInstance();
            SAXParser saxParser = factory.newSAXParser();

            DefaultHandler handler = new DefaultHandler() {

                boolean prefixFlag = false;
                boolean iriflag = false;
                boolean uriflag = false;
                boolean dataEntryflag = false;
                boolean definitionflag = false;
                boolean urisflag = false;
                boolean homepageflag = false;
                boolean titleflag = false;

                public void startElement(String uri, String localName, String qName,
                                         Attributes attributes) throws SAXException {

                    sb = new StringBuilder();

                    if (qName.equalsIgnoreCase("namespace")) {
                        prefixFlag = true;
//                        todo: detect URN and turn flag to false

                    }

                    if (qName.equalsIgnoreCase("uris")) {

                        urisflag = true;

                    }

                    if (qName.equalsIgnoreCase("uri")) {

                        uriflag = true;

                        for (int i = 0; i < attributes.getLength(); i++) {
                            if (attributes.getQName(i).contains("deprecated")) {
//                               todo: capture deprecated stuff too but with a deprecated flag
                                uriflag = false;
                            }
                        }

                    }

                    if (qName.equalsIgnoreCase("dataEntry")) {
                        dataEntryflag = true;
                    }

                    if (qName.equalsIgnoreCase("definition")) {
                        definitionflag = true;
                    }

                    if (qName.equalsIgnoreCase("dataResource")) {
                        homepageflag = true;
                    }

                    if (qName.equalsIgnoreCase("dataInfo")) {
                        titleflag = true;
                    }


                }


                public void endElement(String uri, String localName, String qName)
                        throws SAXException {
                    // TODO Auto-generated method stub
                    String parsedString = sb.toString().trim();

                    if (prefixFlag) {

                        entry.primaryprefix = parsedString;
                        prefixFlag = false;
                    }

                    if (iriflag) {
                        if (!parsedString.startsWith("urn")) {
                            entry.iri = parsedString;
                        }
                        iriflag = false;
                    }

                    if (dataEntryflag) {
                        String resolvingnamespace = parsedString.replace("$id", "#");
                        entry.resolvingnamespaces.add(resolvingnamespace);
                        dataEntryflag = false;
                    }

                    if (definitionflag) {
                        entries.add(entry);
                        entry = new Entry();
                        entry.description = "\""+parsedString.replaceAll("\n"," ")+"\"";
                        definitionflag = false;
                    }


                    if (homepageflag) {
                        entry.homepages.add(parsedString);
                        homepageflag = false;
                    }

                    if (titleflag) {
                        entry.title = ("\""+parsedString+"\"");
                        titleflag = false;
                    }
                }

                public void characters(char ch[], int start, int length) throws SAXException {

                    if (sb != null) {
                        for (int i = start; i < start + length; i++) {
                            sb.append(ch[i]);
                        }
                    }

                }

            };

            saxParser.parse("src/IdentifiersOrg-Registry_2015-11-20T15-46-36+00-00.xml", handler);

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

}