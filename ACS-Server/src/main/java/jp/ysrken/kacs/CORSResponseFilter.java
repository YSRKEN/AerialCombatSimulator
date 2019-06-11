package jp.ysrken.kacs;

import javax.servlet.*;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * CORS対応させるためのフィルター設定 参考：http://seratch.hatenablog.jp/entry/2013/08/13/153415
 * 
 * @author ysrken
 */
public class CORSResponseFilter implements Filter {
	@Override
	public void init(FilterConfig filterConfig) throws ServletException {
	}

	@Override
	public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
			throws IOException, ServletException {
		HttpServletResponse _response = (HttpServletResponse) response;
		_response.setHeader("Access-Control-Allow-Origin", "*");
		_response.setHeader("Access-Control-Allow-Methods", "POST, PUT, GET, DELETE, OPTIONS");
		_response.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
		_response.setHeader("Access-Control-Max-Age", "-1");
		chain.doFilter(request, _response);
	}

	@Override
	public void destroy() {
	}
}
