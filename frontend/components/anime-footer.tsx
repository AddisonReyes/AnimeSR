const REPOSITORY_URL = "https://github.com/AddisonReyes/Anime-System-Recomendations";
const AUTHOR_URL = "https://addisonreyes.com";

type AnimeFooterProps = {
  apiDocsUrl: string;
  currentYear: number;
};

export function AnimeFooter({ apiDocsUrl, currentYear }: AnimeFooterProps) {
  return (
    <footer className="site-footer">
      <div className="site-footer__meta">
        <p className="site-footer__brand">AnimeSR</p>
        <p className="site-footer__copy">© {currentYear} AnimeSR. All rights reserved.</p>
      </div>
      <div className="site-footer__aside">
        <p className="site-footer__backend-line">
          <a href={apiDocsUrl} rel="noreferrer" target="_blank">
            API
          </a>{" "}
          /{" "}
          <a href={REPOSITORY_URL} rel="noreferrer" target="_blank">
            Code
          </a>
        </p>
        <p className="site-footer__credit">
          Made by{" "}
          <a href={AUTHOR_URL} rel="noreferrer" target="_blank">
            Addison Reyes
          </a>
        </p>
      </div>
    </footer>
  );
}
