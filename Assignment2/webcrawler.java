import java.net.*;
import java.io.*;
import java.lang.String;
import java.util.List;
import java.util.ArrayList;
import java.util.Vector;
import java.util.Scanner;
import java.util.Map;
public class webcrawler {
	public static void main(String[] args) {

		int port = 80;


		Vector<String> explored = new Vector<String>();
			try {
				System.out.println(args[0]);
				Scanner sc = new Scanner(System.in);
				int i = sc.nextInt();

//				Socket sock = new Socket();
//				OutputStream theOutput = sock.getOutputStream();
//				DataOutputStream out = new DataOutputStream(sock.getOutputStream());
//				StringBuilder sb = new StringBuilder();
//				InputStream in = sock.getInputStream();
//				InputStreamReader isr = new InputStreamReader(in);
//				BufferedReader br = new BufferedReader(isr);
				String str;
				Vector<String> unexplored = new Vector<String>();
				unexplored.add(args[0]);
				int c;
				while (unexplored.size()>0){
//					String params = URLEncoder.encode("param1", "UTF-8")
//							+ "=" + URLEncoder.encode("value1", "UTF-8");
//
//					params += "&" + URLEncoder.encode("param2", "UTF-8")
//							+ "=" + URLEncoder.encode("value2", "UTF-8");
					String url_string = unexplored.get(0);
					URL url = new URL(url_string);
					//URL obj = new URL("http://mkyong.com");
					URLConnection conn = url.openConnection();
					
					//get all headers
					Map<String, List<String>> map = conn.getHeaderFields();
					for (Map.Entry<String, List<String>> entry : map.entrySet()) {
						System.out.println("Key : " + entry.getKey() + 
				                 " ,Value : " + entry.getValue());
					}
	
					//String header = readHeader(url.getHost());
					System.out.println("Using URL: " + url.getHost());
					System.out.println("Using port: " + url.getPort());
					String path_file = getPathFile(url_string, url.getPort());
					System.out.println("Using path: " + path_file);
					unexplored.remove(0);
					explored.add(url_string);
					if (url.getPort() != -1) port = url.getPort();
					if (!(url.getProtocol().equalsIgnoreCase("http"))) {
						System.err.println("Sorry. I only understand http.");
						continue;
					}
					Socket sock = new Socket(url.getHost(), port);
					System.out.print("!!!!!!!!!!!!!!!!!!!!!!!!!");
					System.out.print(url.getHost());

					OutputStream theOutput = sock.getOutputStream();
//					DataOutputStream out = new DataOutputStream(sock.getOutputStream());
					PrintWriter writer = new PrintWriter(theOutput, true);
					writer.println("GET " + url.getPath() + "\r\n" + " HTTP/1.0\r\n");
					writer.println("Host: " + url.getHost() + "\r\n");
					writer.println("User-Agent: Simple Http Client" + "\r\n");
					writer.println("Accept: text/html" + "\r\n");
					writer.println("Accept-Language: en-US" + "\r\n");
					writer.println("Connection: Keep-Alive" + "\r\n");
					writer.println();
					writer.flush();
//					String entireURL = "GET " + path_file + "\r\n" + "HTTP/1.1\r\n";
//					out.write(entireURL.getBytes());
					StringBuilder sb = new StringBuilder();
					InputStream in = sock.getInputStream();
					InputStreamReader isr = new InputStreamReader(in);
					BufferedReader br = new BufferedReader(isr);
					while ((c = br.read()) != -1) {
						//System.out.print((char) c);
						sb.append((char) c);
					}
					str = sb.toString();
					System.out.println(str);
					int si = str.indexOf("href=\"");
					int fi = str.indexOf("\">", si);
					while (si >= 0){
//						System.out.println("si : " + si);
//						System.out.println("fi : " + fi);
						String new_str = str.substring(si+6,fi);//returns va
						if (!explored.contains(new_str) && !unexplored.contains(new_str)) {
							//System.out.println("Adding url: " + new_str + " to unexplored.");
							unexplored.add(new_str);
						}
						//System.out.println(new_str);
						si = str.indexOf("href=\"", fi);
						fi = str.indexOf("\">", si);
					}
					sock.close();
				}
			} catch (MalformedURLException ex) {
				System.err.println(args[0] + " is not a valid URL");
			} catch (IOException ex) {
//				sock.close();
//				out.close();
				System.out.println("Explored URLs are: ");
				for (int i=0; i<explored.size(); i++)
					System.out.println(explored.get(i));
				System.err.println(ex);
			}


	}
	public static String getPathFile(String url, int port){
		String port_string = String.valueOf(port);
		int si = url.indexOf(port_string);
		String return_str = url.substring(si+port_string.length());
		if (return_str.length()>=1)
			return return_str;
		else
			return "/";
	}
//	public  static String readHeader(String url_str){
//		URL url = new URL(url_str);
//		return url_str;
//	}

}


